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

    $('#projects_table tbody').on('click', '.delete_project', function () {
        let project_id = $(this).data('project_id');
        let url = '/project/projects/ajax/' + project_id + '/delete/';
        Swal({
            title: "确定删除项目",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定",
            cancelButtonText: "取消",
        }).then(function (result) {
            if (result.value) {
                $.post(url, {}, function (data) {
                    if (data.status) {
                        //Swal('成功', '成功删除项目', 'success').then(function () {
                        //window.location.reload();
                        //});
                        toastr.success('成功删除项目');
                        refresh(500);
                    } else {
                        //Swal('出错', data.errmsg, 'error').then(function () {
                        //window.location.reload();
                        //});
                        toastr.error('删除项目出错:' + data.errmsg);
                    }
                })
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    });

    $('#projects_table tbody').on('click', '.sync_project', function () {
        let project_id = $(this).data('project_id');
        let url = '/project/projects/ajax/' + project_id + '/sync/';
        Swal({
            title: "请输入密码进行同步",
            input: "password",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            preConfirm: function (password) {
                return {password: password}
            }
        }).then(function (result) {
            if (result.value) {
                let password = result.value.password;
                data = {
                    data: JSON.stringify(
                        {
                            password: password,
                        }
                    )
                };
                if (password.length === 0 || password === undefined || password === null) {
                    toastr.error('请输入密码');
                    //Swal('提示', '输入的密码为空', 'info').then(function () {
                    //});
                } else {
                    $.post(url, data, function (data) {
                        if (data.status) {
                            //Swal('成功', '成功同步项目', 'success').then(function () {
                            //window.location.reload();
                            //});
                            toastr.success('成功同步项目');
                            refresh(500);
                        } else {
                            //Swal('出错', data.errmsg, 'error').then(function () {
                                //window.location.reload();
                            //});
                            toastr.error('同步项目出错:'+data.errmsg);
                        }
                    })
                }
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    });
});