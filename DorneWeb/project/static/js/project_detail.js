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

    $('.sync_project').click(function () {
        let project_id = $(this).data('project_id');
        console.log('project_id', project_id);
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
                console.log('password', password);
                data = {
                    data: JSON.stringify(
                        {
                            password: password,
                        }
                    )
                };
                if (password.length === 0 || password === undefined || password === null) {
                    //Swal('提示', '输入的密码为空', 'info').then(function () {
                    //});
                    toastr.error('请输入密码');
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
                            toastr.error('同步项目出错:'+data.errmsg)
                        }
                    })
                }
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    });
});