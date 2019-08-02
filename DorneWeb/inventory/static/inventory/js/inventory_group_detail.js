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
    $('.selectpicker').selectpicker();
    
    $('#pill_groups').addClass('active');

    toastr.options = {
        positionClass: "toast-bottom-right",
        // preventDuplicates: true
    };

    $('#group_detail_vars_format').click(function() {
        vars_format('#group_detail_form textarea[name="vars"]');
    });

    // edit group
    $('#group_detail_submit_btn').click(function() {
        let result = true;
        result = validate_group_name(
            '#group_detail_form input[name="name"]',
            '#group_detail_form #group_name_err'
        ) && result;
        result = validate_group_description(
            '#group_detail_form textarea[name="description"]',
            '#group_detail_form #group_description_err'
        ) && result;
        result = validate_group_vars(
            '#group_detail_form textarea[name="vars"]',
            '#group_detail_form #group_vars_err'
        ) && result;

        if (result) {
            vars_format('#group_detail_form textarea[name="vars"]');
            let data = {
                name: $('#group_detail_form input[name="name"]').val(),
                description: $('#group_detail_form textarea[name="description"]').val(),
                vars: $('#group_detail_form textarea[name="vars"]').val()
            };
            $.post($(this).data('path'), data, function(result) {
                if (result.status) {
                    toastr.success('已修改组');

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

    $('#host_table').on('click', '.remove_host', function(){
        $('#remove_host_form>input[name=host_id]').val($(this).data('host_id'));
        $('#remove_host_form').submit();
        return false;
    });
    
    $('#group_table').on('click', '.remove_group', function(){
        $('#remove_group_form>input[name=cgid]').val($(this).data('group_id'));
        $('#remove_group_form').submit();
        return false;
    });
});