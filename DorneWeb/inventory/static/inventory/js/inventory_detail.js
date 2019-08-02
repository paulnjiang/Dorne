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
    $('#pill_detail').addClass('active');

    toastr.options = {
        positionClass: "toast-bottom-right",
        // preventDuplicates: true
    };

    $('#inv_vars_format').click(function() {
        vars_format('#inv_detail_form textarea[name="vars"]');
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
});