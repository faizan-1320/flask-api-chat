import math

def pagenation_common(page,limit):
    page = int(page)
    limit = int(limit)
    start = (page * limit) - limit
    start = str(start)
    return start

def common_response(result,page_size,page_count):
    response = {'message':'Success','page_size':10, 'per_page_record':page_size, 'page_count':page_count, 'result':result}
    return response

def page_count(page_size,limit):
    page_size = int(page_size)
    limit = int(limit)
    page_count = page_size/limit
    ceil_value  = math.ceil(page_count)
    return ceil_value