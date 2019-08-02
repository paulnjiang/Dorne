$(function () {
    toastr.options = {
        'positionClass': 'toast-bottom-right',
        'preventDuplicates': true
    };
    $("#user_role_add_btn").click(function () {
        // Project相关
        let project_ids = [];
        $("#project_table_tbody input[type='checkbox']").each(function () {
            if ($(this).prop('checked')) {
                project_id = $(this).parent().parent().attr("id");
                project_ids.push(project_id)
            }
        });
        let project_role = $("#project_role_select_id").val();
        if (project_ids.length !== 0) {
            if (project_role === null || project_role === undefined || project_role.length === 0) {
                //Swal("提示", "请为项目选择角色", "Info");
                toastr.error('请为项目选择角色');
                return;
            }
        }
        //Inventory相关
        let inventory_ids = [];
        $("#inventory_table_tbody input[type='checkbox']").each(function () {
            if ($(this).prop("checked")) {
                inventory_id = $(this).parent().parent().attr("id");
                inventory_ids.push(inventory_id);
            }
        });
        console.log('inventory_ids', inventory_ids);
        let inventory_role = $("#inventory_role_select_id").val();
        if (inventory_ids.length !== 0) {
            if (inventory_role === null || inventory_role === undefined || inventory_role.length === 0) {
                //Swal("提示", "请为Inventory选择角色", "info");
                toastr.error('请为仓库选择角色');
                return;
            }
        }
        //Template相关
        let template_ids = [];
        $("#template_table_tbody input[type='checkbox']").each(function () {
            if ($(this).prop("checked")) {
                template_id = $(this).parent().parent().attr("id");
                template_ids.push(template_id);
            }
        });
        let template_role = $("#template_role_select_id").val();
        if (template_ids.length !== 0) {
            if (template_role === null || template_role === undefined || template_role.length === 0) {
                //Swal("提示", "请为Template选择角色", "info");
                toastr.error('请为任务模板选择角色');
                return;
            }
        }

        // System相关
        let system_admin = false;
        $("#system_table_tbody input[type='checkbox']").each(function () {
            if ($(this).prop("checked")) {
                system_admin = true;
            }
        });

        if (project_ids.length === 0 && inventory_ids.length === 0
            && template_ids.length === 0 && system_admin === false) {
            //Swal("提示", "请选择至少一个资源", "info");
            toastr.error('请选择至少一个资源');
            return;
        }
        let target_user_id = $("#target_user").data("target_user_id");

        args = {
            'project_ids': project_ids,
            'project_role': project_role,
            'inventory_ids': inventory_ids,
            'inventory_role': inventory_role,
            'template_ids': template_ids,
            'template_role': template_role,
            //'organization_ids': organization_ids,
            //'organization_role': organization_role,
            'system_admin': system_admin
        };
        console.log(args);
        let data = JSON.stringify(args);
        params = {
            'data': data
        };
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
                $.post("/user/users/" + target_user_id + "/role/add/", params, function (data) {
                    if (data.status) {
                        toastr.success('添加成功');
                        setTimeout(function(){
                            window.location.href = '/user/users/'+target_user_id+"/role/";
                        }, 1000);
                    } else {
                        //Swal("失败", "添加角色失败:" + data.errmsg, "error").then(function () {
                            //window.location.reload();
                        //})
                        toastr.error('添加失败:'+data.errmsg);
                    }
                })
            } else if (result.dismiss === Swal.DismissReason.cancel) {
            }
        });

    });
});
