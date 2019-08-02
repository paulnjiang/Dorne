function formatter_inv_name(value, row, index) {
    return '<a href="' + row.path + '">' + value + '</a>';
}

function formatter_inv_organization(value, row, index) {
    return '<a href="' + row.organization.path + '">' + value + '</a>';
}

function formatter_inv_operation(value, row, index) {
    let result = '';
    
    if (row.pm.delete_inventory) {
        result += 
            '<a class="dorne-action inv_delete_btn" data-path_api_delete="'
            + row.path_api_delete
            + '" data-inv_id="'
            + row.id
            + '" title="删除"><span class="glyphicon glyphicon-trash"></span></a>';
    }
    return result;
}

function inv_vars_format() {
    try {
        let result = $.parseJSON($('textarea[name=vars]').val());
        $('textarea[name=vars]').val(JSON.stringify(result, null, 4));
        return true;
    }
    catch (e) {
        return false;
    }
}

function reset_page() {
    // $('#inv_create_panel').slideUp(382);
    $('#inv_create_panel').hide();
    $('#invs_panel').show();
    $('#inv_create_form')[0].reset();
    $('#inv_create_form .selectpicker').selectpicker('val', '');
    $('#inv_create_alert').hide();
    $('#inv_table').bootstrapTable('refresh', {silent: true});
}


$(function() {
    $('.selectpicker').selectpicker();

    toastr.options = {
        positionClass: "toast-bottom-right",
        // preventDuplicates: true
    };

    $('#inv_table').on('click', '.inv_delete_btn', function(){
        Swal.fire({
            title: "确定删除？",
            // type: "warning",
            showCancelButton: true,
            confirmButtonText: "确定",
            cancelButtonText: "取消",
        }).then((result) => {
            if (result.value) {
                $.post($(this).data('path_api_delete'), {inventory_id: parseInt($(this).data('inv_id'))}, function(result) {
                    if (result.status) {
                        toastr.success('已删除仓库');
                        $('#inv_table').bootstrapTable('refresh', {silent: true});
                    }
                    else {
                        toastr.error(result.msg);
                    }
                });
            }
        });
        
        return true;
    });

    $('#inv_create_panel_toggle_btn').click(function() {
        // $('#inv_create_panel').slideDown(382);
        $('#inv_create_panel').show();
        $('#invs_panel').hide();
    });

    $('#inv_create_panel_close_btn').click(function() {
        // $('#inv_create_panel').slideUp(382);
        $('#inv_create_panel').hide();
        $('#invs_panel').show();
    });

    $('#vars_format').click(inv_vars_format);

    // validate then submit data to create a new inventory
    $('#inv_create_submit_btn').click(function() {
        let result = true;
        result = validate_inv_name('input[name="name"]', '#inv_name_err') && result;
        result = validate_inv_organization_id('select[name="organization_id"]', '#inv_organization_id_err') && result;
        result = validate_inv_description('textarea[name="description"]', '#inv_description_err') && result;
        result = validate_inv_vars('textarea[name="vars"]', '#inv_vars_err') && result;

        if (result) {
            inv_vars_format();
            let data = {
                name: $('input[name="name"]').val(),
                organization_id: parseInt($('select[name="organization_id"]').val()),
                description: $('textarea[name="description"]').val(),
                vars: $('textarea[name="vars"]').val()
            };
            $.post($(this).data('path'), data, function(result) {
                if (result.status) {
                    reset_page();
                    toastr.success('已创建仓库');

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
});