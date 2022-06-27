from .. import base_views

category_id = 2
base_dir = {'base_template': 'boards/school/',
            'base_url': 'boards:school_'}
def board_list(request):
    render = base_views.board_list(request, category_id, base_dir)
    return render

def board_detail(request, board_id):
    render = base_views.board_detail(request, board_id, base_dir)
    return render

def board_create(request):
    render = base_views.board_create(request, category_id, base_dir)
    return render

def posting_detail(request, posting_id):
    render = base_views.posting_detail_on_board(request, posting_id, base_dir)
    return render

def posting_create(request, board_id):
    render = base_views.posting_create_on_board(request, board_id, base_dir)
    return render
def posting_modify(request, posting_id):
    render = base_views.posting_modify_on_board(request, posting_id, base_dir)
    return render