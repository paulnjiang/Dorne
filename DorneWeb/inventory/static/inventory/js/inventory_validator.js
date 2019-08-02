function validate_inv_name(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);
    
    let v = node.val();
    
    if (v.length < 4 || v.length > 32) {
        errmsg_node.text('名称长度必须为4～32个字符');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_inv_organization_id(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = parseInt(node.val());
    
    if (isNaN(v)) {
        errmsg_node.text('仓库必须属于一个组织');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_inv_description(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();
    
    if (v.length > 128) {
        errmsg_node.text('描述长度必须小于等于128个字符');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_inv_vars(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();

    if (v != '') {
        try {
            $.parseJSON(v);
        }
        catch (e) {
            errmsg_node.text('变量必须为JSON格式的数据');
            return false;
        }
    }

    errmsg_node.text('');
    return true;
}

function validate_host_name(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();
    
    if (v.length < 4 || v.length > 64) {
        errmsg_node.text('名称长度必须为4～64个字符');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_host_ip(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();
    let ipv4_regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    let ipv6_regex = /^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$/;
    
    if (!ipv4_regex.test(v) && !ipv6_regex.test(v)) {
        errmsg_node.text('IP地址非法');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_host_description(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();
    
    if (v.length > 128) {
        errmsg_node.text('描述长度必须小于等于128个字符');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_host_vars(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();

    if (v != '') {
        try {
            $.parseJSON(v);
        }
        catch (e) {
            errmsg_node.text('变量必须为JSON格式的数据');
            return false;
        }
    }

    errmsg_node.text('');
    return true;
}

function validate_group_name(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();
    
    if (v.length < 4 || v.length > 64) {
        errmsg_node.text('名称长度必须为4～64个字符');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_group_description(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();
    
    if (v.length > 128) {
        errmsg_node.text('描述长度必须小于等于128个字符');
        return false;
    }

    errmsg_node.text('');
    return true;
}

function validate_group_vars(node_selector, errmsg_selector) {
    let node = $(node_selector), errmsg_node = $(errmsg_selector);

    let v = node.val();

    if (v != '') {
        try {
            $.parseJSON(v);
        }
        catch (e) {
            errmsg_node.text('变量必须为JSON格式的数据');
            return false;
        }
    }

    errmsg_node.text('');
    return true;
}