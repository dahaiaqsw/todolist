$('#add_todo').click(function () {
    inp_element = $(this).siblings('input');
    if(inp_element.val().trim() != ''){
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=UTF-8',
            url: '/add',
            data: JSON.stringify({'todo': inp_element.val()}),
            success: function (data) {
                if(data=='added'){
                    inp_element.val('');
                    $('#outer').load('/index #inner');
                };
            }
    })
    }else{
        alert('代办事项不能为空！')
    }
});

function finish(e){
    id = e.siblings('input').val();
    $.ajax({
        type: 'POST',
        contentType: 'application/json; charset=UTF-8',
        url: '/finish',
        data: JSON.stringify({'_id': id}),
        success: function (data) {
            $('#outer').load('/index #inner');
        }
    })
};

function del(e){
    id = e.siblings('input').val();
    $.ajax({
        type: 'POST',
        contentType: 'application/json; charset=UTF-8',
        url: '/delete',
        data: JSON.stringify({'_id': id}),
        success: function (data) {
            $('#outer').load('/index #inner');
            }
        }
    )
};

