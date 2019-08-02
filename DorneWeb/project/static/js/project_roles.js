$(function () {
    toastr.options = {
        'positionClass': 'toast-bottom-right',
        'preventDuplicates': true
    };

    function refresh(time) {
        setTimeout(
            function () {
                window.location.reload();
            }, time)
    }

    $('#project_user_role_table tbody').on('click', '.remove_user_role', function () {
        let project_id = $('#project_id').data('project_id');
        let role_id = $(this).data('role_id');
        let user_id = $(this).data('user_id');

        let url = '/project/projects/ajax/' + project_id + '/roles/remove/';
        Swal({
            title: "确定删除",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定",
            cancelButtonText: "取消",
        }).then(function (result) {
            if (result.value) {
                let data = {
                    data: JSON.stringify({
                        target: 'user',
                        role_id: role_id,
                        user_id: user_id,
                    })
                };
                $.post(url, data, function (data) {
                    if (data.status) {
                        //Swal('成功', '角色删除成功', 'success').then(function () {
                           //window.location.reload();
                        //});
                        toastr.success('角色删除成功');
                        refresh(500);
                    } else {
                        //Swal('出错', data.errmsg, 'error').then(function () {
                            //window.location.reload();
                        //});
                        toastr.error('角色删除出错:' + data.errmsg)
                    }
                })
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    });

    $('#project_team_role_table tbody').on('click', '.remove_team_role', function () {
        let project_id = $('#project_id').data('project_id');
        let role_id = $(this).data('role_id');
        let team_id = $(this).data('team_id');
        let url = '/project/projects/ajax/' + project_id + '/roles/remove/';
        Swal({
            title: "确定删除",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定",
            cancelButtonText: "取消",
        }).then(function (result) {
            if (result.value) {

                let data = {
                    data: JSON.stringify({
                        target: 'user',
                        role_id: role_id,
                        team_id: team_id,
                    })
                };
                $.post(url, data, function (data) {
                    if (data.status) {
                        //Swal('成功', '角色删除成功', 'success').then(function () {
                           //window.location.reload();
                        //});
                        toastr.success('角色删除成功');
                    } else {
                        //Swal('出错', data.errmsg, 'error').then(function () {
                            //window.location.reload();
                        //});
                        toastr.error('角色删除出错:' + data.errmsg)
                    }
                })
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    });
});