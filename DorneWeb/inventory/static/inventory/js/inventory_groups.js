function formatter_group_name(value, row, index) {
    return '<a href="' + row.path_detail + '">' + value + '</a>';
}

function formatter_group_operation(value, row, index) {
    let result = '';
    
    if (row.pm.delete_group) {
        result += 
            '<a class="dorne-action group_delete_btn" data-path="'
            + row.path_api_delete
            + '" data-group_id="'
            + row.id
            + '" title="删除"><span class="glyphicon glyphicon-trash"></span></a>';
    }
    return result;
}

function vars_format(node) {
    try {
        let vars = $(node);
        let result = $.parseJSON(vars.val());
        vars.val(JSON.stringify(result, null, 4));
        return true;
    }
    catch (e) {
        return false;
    }
}

function group_reset_page() {
    $('#group_create_panel').hide();
    $('#groups_panel').show();
    $('#group_create_form')[0].reset();
    $('#group_table').bootstrapTable('refresh', {silent: true});
}


$(function() {
    $('#pill_groups').addClass('active');

    toastr.options = {
        positionClass: "toast-bottom-right",
        // preventDuplicates: true
    };

    $('#group_create_vars_format').click(function() {
        vars_format('#group_create_form textarea[name="vars"]');
    });

    $('#group_create_panel_toggle_btn').click(function() {
        $('#group_create_panel').show();
        $('#groups_panel').hide();
    });

    $('#group_create_panel_close_btn').click(function() {
        $('#group_create_panel').hide();
        $('#groups_panel').show();
    });

    // create group
    $('#group_create_submit_btn').click(function() {
        let result = true;
        result = validate_group_name(
            '#group_create_form input[name="name"]',
            '#group_create_form #group_name_err'
        ) && result;
        result = validate_group_description(
            '#group_create_form textarea[name="description"]',
            '#group_create_form #group_description_err'
        ) && result;
        result = validate_group_vars(
            '#group_create_form textarea[name="vars"]',
            '#group_create_form #group_vars_err'
        ) && result;

        if (result) {
            vars_format('#group_create_form textarea[name="vars"]');
            let data = {
                name: $('#group_create_form input[name="name"]').val(),
                description: $('#group_create_form textarea[name="description"]').val(),
                vars: $('#group_create_form textarea[name="vars"]').val(),
                inventory_id: parseInt($(this).data('inventory_id'))
            };
            $.post($(this).data('path'), data, function(result) {
                if (result.status) {
                    toastr.success('已创建组');
                    group_reset_page();

                    return true
                }
                else {
                    toastr.error(result.msg);
                    
                    return false;
                }
            });
        }

        return false;
    });

    // delete group
    $('#group_table').on('click', '.group_delete_btn', function(){
        Swal.fire({
            title: "确定删除？",
            // type: "warning",
            showCancelButton: true,
            confirmButtonText: "确定",
            cancelButtonText: "取消",
        }).then((result) => {
            if (result.value) {
                $.post($(this).data('path'), {group_id: parseInt($(this).data('group_id'))}, function(result) {
                    if (result.status) {
                        toastr.success('已删除组');
                        $('#group_table').bootstrapTable('refresh', {silent: true});
                    }
                    else {
                        toastr.error(result.msg);
                    }
                });
            }
        });
        
        return true;
    });
});