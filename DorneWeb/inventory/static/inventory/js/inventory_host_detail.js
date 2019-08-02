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


$(function() {
    $('#pill_hosts').addClass('active');

    toastr.options = {
        positionClass: "toast-bottom-right",
        // preventDuplicates: true
    };

    $('#host_detail_vars_format').click(function() {
        vars_format('#host_detail_form textarea[name="vars"]');
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