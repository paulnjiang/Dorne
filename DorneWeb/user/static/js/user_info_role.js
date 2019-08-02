$(function () {
    toastr.options = {
        'positionClass': 'toast-bottom-right',
        'preventDuplicates': true
    };

    function refresh(time) {
        setTimeout(
            function () {
                window.location.reload();
            }, time);
    }

    $("#user_role_tbody tr").on('click', '.remove_user_role', function () {
        let target_user_id = $('#target_user_id_label').data('target_user_id');
        let role_id = $(this).data('role_id');
        let url = '/user/users/ajax/role/remove/';
        let args = {
            target_user_id: target_user_id,
            role_id: role_id
        };
        let data = {
            data: JSON.stringify(args)
        };

        Swal({
            title: "确定删除角色",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            closeOnConfirm: false
        }).then(function (result) {
            if (result.value) {
                $.post(url, data, function (data) {
                    if (data.status) {
                        //Swal('成功', '删除成功', 'success').then(function () {
                        //window.location.reload();
                        //})
                        toastr.success('删除成功');
                        refresh(500);
                    } else {
                        toastr.error('删除出错:'+data.errmsg);
                    }
                })
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    })
});