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

function formatter_host_name(value, row, index) {
    return '<a class="host_detail_btn" data-path_api_detail="' + row.path_api_detail + '">' + value + '</a>';
}

function formatter_host_operation(value, row, index) {
    let result = '';
    
    if (row.pm.delete_host) {
        result += 
            '<a class="dorne-action host_delete_btn" data-path_api_delete="'
            + row.path_api_delete
            + '" data-host_id="'
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

function host_reset_page() {
    $('#host_create_panel').hide();
    $('#hosts_panel').show();
    $('#host_create_form')[0].reset();
    $('#host_table').bootstrapTable('refresh', {silent: true});
}


$(function() {
    $('.selectpicker').selectpicker();

    toastr.options = {
        positionClass: "toast-bottom-right",
        // preventDuplicates: true
    };

    $('#inv_vars_format').click(function() {
        vars_format('#inv_detail_form textarea[name="vars"]');
    });

    $('#host_create_panel_toggle_btn').click(function() {
        $('#host_create_panel').show();
        $('#hosts_panel').hide();
    });

    $('#host_create_panel_close_btn').click(function() {
        $('#host_create_panel').hide();
        $('#hosts_panel').show();
    });
    $('#host_detail_panel_close_btn').click(function() {
        $('#host_detail_panel').hide();
        $('#hosts_panel').show();
    });

    // validate the submit data to create a new inventory
    $('#inv_detail_submit_btn').click(function() {
        let result = true;
        result = validate_inv_name(
            '#inv_detail_form input[name="name"]',
            '#inv_name_err'
        ) && result;
        result = validate_inv_description(
            '#inv_detail_form textarea[name="description"]',
            '#inv_description_err'
        ) && result;
        result = validate_inv_vars(
            '#inv_detail_form textarea[name="vars"]',
            '#inv_vars_err'
        ) && result;

        if (result) {
            vars_format('#inv_detail_form textarea[name="vars"]');
            let data = {
                name: $('#inv_detail_form input[name="name"]').val(),
                description: $('#inv_detail_form textarea[name="description"]').val(),
                vars: $('#inv_detail_form textarea[name="vars"]').val()
            };
            $.post($(this).data('path'), data, function(result) {
                if (result.status) {
                    toastr.success('已修改仓库');

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

    // create host
    $('#host_create_submit_btn').click(function() {
        let result = true;
        result = validate_host_name(
            '#host_create_form input[name="name"]',
            '#host_create_form #host_name_err'
        ) && result;
        result = validate_host_ip(
            '#host_create_form input[name="ip"]',
            '#host_create_form #host_ip_err'
        ) && result;
        result = validate_host_description(
            '#host_create_form textarea[name="description"]',
            '#host_create_form #host_description_err'
        ) && result;
        result = validate_host_vars(
            '#host_create_form textarea[name="vars"]',
            '#host_create_form #host_vars_err'
        ) && result;

        if (result) {
            vars_format('#host_create_form textarea[name="vars"]');
            let data = {
                name: $('#host_create_form input[name="name"]').val(),
                ip: $('#host_create_form input[name="ip"]').val(),
                description: $('#host_create_form textarea[name="description"]').val(),
                vars: $('#host_create_form textarea[name="vars"]').val(),
                inventory_id: parseInt($(this).data('inventory_id'))
            };
            $.post($(this).data('path'), data, function(result) {
                if (result.status) {
                    toastr.success('已创建主机');
                    host_reset_page();

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

    // edit host
    $('#host_detail_submit_btn').click(function() {
        let result = true;
        result = validate_host_name(
            '#host_detail_form input[name="name"]',
            '#host_detail_form #host_name_err'
        ) && result;
        result = validate_host_ip(
            '#host_detail_form input[name="ip"]',
            '#host_detail_form #host_ip_err'
        ) && result;
        result = validate_host_description(
            '#host_detail_form textarea[name="description"]',
            '#host_detail_form #host_description_err'
        ) && result;
        result = validate_host_vars(
            '#host_detail_form textarea[name="vars"]',
            '#host_detail_form #host_vars_err'
        ) && result;

        if (result) {
            vars_format('#host_detail_form textarea[name="vars"]');
            let data = {
                name: $('#host_detail_form input[name="name"]').val(),
                ip: $('#host_detail_form input[name="ip"]').val(),
                description: $('#host_detail_form textarea[name="description"]').val(),
                vars: $('#host_detail_form textarea[name="vars"]').val()
            };
            $.post($(this).data('path'), data, function(result) {
                if (result.status) {
                    toastr.success('已修改主机');
                    $('#host_table').bootstrapTable('refresh', {silent: true});

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

    $('#host_table').on('click', '.host_detail_btn', function() {
        $('#host_detail_form')[0].reset();
        $('#host_detail_submit_btn').data('path', '');
        $('#host_detail_panel').show();
        $('#hosts_panel').hide();
        $.get($(this).data('path_api_detail'), function(result) {
            if (result.status) {
                $('#host_detail_form input[name="name"]').val(result.host.name);
                $('#host_detail_form input[name="ip"]').val(result.host.ip);
                $('#host_detail_form textarea[name="description"]').val(result.host.description);
                $('#host_detail_form textarea[name="vars"]').val(result.host.vars);
                $('#host_detail_submit_btn').data('path', result.host.path_api_edit);

                return true;
            }
            else {
                toastr.error(result.msg);
                $('#host_detail_panel').hide();
                $('#hosts_panel').show();

                return false;
            }
        });
    });

    // delete host
    $('#host_table').on('click', '.host_delete_btn', function(){
        Swal.fire({
            title: "确定删除？",
            type: "warning",
            showCancelButton: true,
            confirmButtonText: "确定",
            cancelButtonText: "取消",
        }).then((result) => {
            if (result.value) {
                $.post($(this).data('path_api_delete'), {host_id: parseInt($(this).data('host_id'))}, function(result) {
                    if (result.status) {
                        toastr.success('已删除主机');
                        $('#host_table').bootstrapTable('refresh', {silent: true});
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