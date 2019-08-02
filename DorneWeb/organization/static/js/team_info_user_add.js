$(function () {
    $(".add_user_to_team").click(function () {
        let user_ids = [];
        $("#add_user_to_team_tbody input[type='checkbox']").each(function () {
            if ($(this).prop('checked')) {
                let user_id = $(this).data('user_id');
                user_ids.push(user_id);
            }
        });
        if (user_ids.length === 0) {
            //Swal('请至少选择一个用户', '', 'info');
            toastr.error('请至少选择一个用户');
        } else {
            Swal({
                title: "确定添加",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                closeOnConfirm: false
            }).then(function (result) {
                if (result.value) {
                    let team_role = $('#team_role_select').val();
                    data = JSON.stringify({
                        'team_id': team_id,
                        'user_ids': user_ids,
                        'team_role': team_role
                    });
                    data = {
                        data: data
                    };
                    let url = '/organization/team/info/' + team_id + '/user/add/';
                    $.post(url, data, function (data) {
                        if (data.status) {
                            //Swal('成功', '添加成功', 'success').then(function () {
                                //window.location.href = '/organization/team/info/'+ team_id + '/user/';
                            //})
                            toastr.success('添加成功');
                            refresh(500);
                        } else {
                            //Swal('出错', data.errmsg, 'error').then(function () {
                                //window.location.reload();
                            //})
                            toastr.error('添加出错:' + data.errmsg);
                        }
                    })
                } else if (result.dismiss === Swal.DismissReason.cancel) {

                }
            });
        }
    });


});