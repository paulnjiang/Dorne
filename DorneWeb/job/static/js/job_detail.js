$(function () {

    toastr.options = {
        'positionClass': 'toast-bottom-right',
        'preventDuplicates': true
    };

    $('.delete_job').click(function () {
        let job_id = $(this).data('job_id');
        let url = '/job/jobs/ajax/delete/';
        let data = {
            data: JSON.stringify({job_id: job_id})
        };
        Swal({
            title: "确定删除任务",
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
                        //Swal('成功', '删除任务成功', 'success').then(function () {
                        //window.location.href = '/job/jobs/';
                        //});
                        toastr.success('删除任务成功');
                        setTimeout(function () {
                            window.location.href = '/job/jobs/';
                        }, 1000);
                    } else {
                        //Swal('出错', data.errmsg, 'error').then(function () {
                        //window.location.reload();
                        //});
                        toastr.error('删除任务出错:' + data.errmsg);
                    }
                })
            } else if (result.dismiss === Swal.DismissReason.cancel) {

            }
        });
    });
});