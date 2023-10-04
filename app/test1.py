bbox = [[207, 165], [391, 165], [391, 201], [207, 201]]
keywords: dict = {
    'hoten': {
        'keyword': 'Họ và tên',
        'coordinates': [[190, 160], [520, 160], [520, 205], [190, 205]]
    },
    'namsinh': {
        'keyword': 'Năm sinh',
        'coordinates': [[390, 180], [510, 180], [510, 235], [390, 235]]
    },
    'noisinh': {
        'keyword': 'Nơi sinh',
        'coordinates': [[230, 220], [610, 220], [610, 260], [230, 260]]
    },
    'gioitinh': {
        'keyword': 'Giới tính',
        'coordinates': [[225, 250], [280, 250], [280, 285], [225, 285]]
    },
    'dantoc': {
        'keyword': 'Dân tộc',
        'coordinates': [[440, 255], [580, 255], [580, 290], [440, 290]]
    },
    'truong': {
        'keyword': 'Học sinh trường',
        'coordinates': [[265, 280], [600, 280], [600, 320], [265, 320]]
    },
    'khoathi': {
        'keyword': 'Khóa thi',
        'coordinates': [[190, 310], [320, 310], [320, 350], [190, 350]]
    },
    'hoidong': {
        'keyword': 'Hội đồng thi',
        'coordinates': [[460, 310], [780, 310], [780, 350], [460, 350]]
    },
    'sohieu': {
        'keyword': 'Số hiệu',
        'coordinates': [[170, 480], [350, 480], [350, 520], [170, 520]]
    },
    'sovaoso': {
        'keyword': 'Số vào sổ cấp bằng',
        'coordinates': [[265, 515], [375, 515], [375, 540], [265, 540]]
    }
}


result = {}
for i in keywords:
    coords = keywords[i]['coordinates']
    if  (coords[0][0] <= bbox[0][0] and coords[0][1] <= bbox[0][1]) \
    and (coords[1][0] >= bbox[1][0] and coords[1][1] <= bbox[1][1]) \
    and (coords[2][0] >= bbox[2][0] and coords[2][1] >= bbox[2][1]) \
    and (coords[3][0] <= bbox[3][0] and coords[3][1] >= bbox[3][1]):
        result[keywords[i]['keyword']] = 'yes'

print(result)