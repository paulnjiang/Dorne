$(function () {
    $("#team_role_tbody tr").on('click', '.remove_team_role', function () {
        let target_team_id = $('#target_team_id_label').data('target_team_id');
        let role_id = $(this).data('role_id');
        let url = '/organization/ajax/team/role/remove/';
        let args = {
            target_team_id: target_team_id,
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
                        //Swal('出错', data.errmsg, 'error').then(function () {
                            //window.location.reload();
                        //})
                        toastr.error('删除出错:' + data.errmsg);
                    }
                })
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    })
});