# -*- coding: utf-8 -*-
"""
智谱AI Token使用量统计工具
分析xlsx费用明细文件，统计各API Key的Token使用情况
"""

import os
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 目标资源包名称
TARGET_BUNDLE = 'GLM Coding Pro V2 - 季'


def analyze_token_usage(file_path):
    """
    分析xlsx文件中的Token使用量

    Args:
        file_path: xlsx文件路径

    Returns:
        dict: 包含分析结果的字典
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)

        # 检查必要的列是否存在
        required_columns = ['apiKey', '账期(自然日)', 'Tokens资源包名称', '用量', '模型产品名称']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                'success': False,
                'error': f'文件缺少必要的列: {", ".join(missing_columns)}'
            }

        # 筛选目标资源包
        filtered = df[df['Tokens资源包名称'] == TARGET_BUNDLE].copy()

        if filtered.empty:
            return {
                'success': False,
                'error': f'文件中没有找到 "{TARGET_BUNDLE}" 资源包的数据'
            }

        # 确保日期格式正确
        filtered['账期(自然日)'] = pd.to_datetime(filtered['账期(自然日)']).dt.strftime('%Y-%m-%d')

        # 按apiKey、日期、模型分组统计
        daily_by_model = filtered.groupby(
            ['apiKey', '账期(自然日)', '模型产品名称']
        )['用量'].sum().reset_index()

        # 按apiKey、日期分组统计（不区分模型）
        daily_total = filtered.groupby(
            ['apiKey', '账期(自然日)']
        )['用量'].sum().reset_index()

        # 计算每个apiKey的总使用量
        total_by_key = filtered.groupby('apiKey')['用量'].sum().to_dict()

        # 获取所有日期
        all_dates = sorted(filtered['账期(自然日)'].unique())

        # 按API Key组织数据
        result = {}
        for api_key in total_by_key.keys():
            key_data = daily_by_model[daily_by_model['apiKey'] == api_key]

            # 按日期组织
            daily_data = {}
            for date in all_dates:
                date_rows = key_data[key_data['账期(自然日)'] == date]
                if not date_rows.empty:
                    daily_data[date] = []
                    for _, row in date_rows.iterrows():
                        daily_data[date].append({
                            'model': row['模型产品名称'],
                            'usage': int(row['用量'])
                        })

            result[api_key] = {
                'total': int(total_by_key[api_key]),
                'daily': daily_data
            }

        # 计算总使用量
        grand_total = int(sum(total_by_key.values()))

        return {
            'success': True,
            'data': result,
            'dates': all_dates,
            'grand_total': grand_total,
            'bundle_name': TARGET_BUNDLE
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'分析文件时出错: {str(e)}'
        }


def export_to_csv(data):
    """导出数据为CSV格式"""
    import io

    output = io.StringIO()

    # 写入表头
    output.write('API Key,日期,模型,Token使用量\n')

    # 写入数据
    for api_key, key_data in data['data'].items():
        for date, models in key_data['daily'].items():
            for item in models:
                output.write(f'{api_key},{date},{item["model"]},{item["usage"]}\n')

    output.seek(0)
    return output


def export_to_excel(data):
    """导出数据为Excel格式"""
    import io

    output = io.BytesIO()

    # 准备数据
    rows = []
    for api_key, key_data in data['data'].items():
        for date, models in key_data['daily'].items():
            for item in models:
                rows.append({
                    'API Key': api_key,
                    '日期': date,
                    '模型': item['model'],
                    'Token使用量': item['usage']
                })

    df = pd.DataFrame(rows)

    # 添加汇总行
    for api_key, key_data in data['data'].items():
        rows.append({
            'API Key': api_key,
            '日期': '小计',
            '模型': '-',
            'Token使用量': key_data['total']
        })

    rows.append({
        'API Key': '总计',
        '日期': '-',
        '模型': '-',
        'Token使用量': data['grand_total']
    })

    df = pd.DataFrame(rows)
    df.to_excel(output, index=False, sheet_name='Token使用量统计')
    output.seek(0)

    return output


@app.route('/')
def index():
    """主页"""
    return render_template('index.html', bundle_name=TARGET_BUNDLE)


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和分析"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有选择文件'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'})

    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'error': '请上传Excel文件（.xlsx或.xls）'})

    try:
        # 保存到临时文件
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f'token_analysis_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx')
        file.save(temp_path)

        # 分析文件
        result = analyze_token_usage(temp_path)

        # 删除临时文件
        try:
            os.remove(temp_path)
        except:
            pass

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': f'处理文件时出错: {str(e)}'})


@app.route('/export/csv', methods=['POST'])
def export_csv():
    """导出CSV"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '没有数据'})

    output = export_to_csv(data)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'token_usage_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@app.route('/export/excel', methods=['POST'])
def export_excel():
    """导出Excel"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '没有数据'})

    output = export_to_excel(data)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'token_usage_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )


if __name__ == '__main__':
    print(f'智谱AI Token使用量统计工具')
    print(f'筛选资源包: {TARGET_BUNDLE}')
    print(f'访问地址: http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
