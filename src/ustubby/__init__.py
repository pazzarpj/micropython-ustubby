import inspect
import types
import csv

__version__ = "0.1.0"


def string_template(base_str):
    def string_handle(*args, **kwargs):
        return base_str.format(*args, **kwargs)

    return string_handle


def expand_newlines(lst_in):
    new_list = []
    for line in lst_in:
        new_list.extend(line.replace('\t', '    ').split('\n'))
    return new_list


type_handler = {
    int: string_template("\tmp_int_t {0} = mp_obj_get_int({0}_obj);"),
    float: string_template("\tmp_float_t {0} = mp_obj_get_float({0}_obj);"),
    bool: string_template("\tbool {0} = mp_obj_is_true({0}_obj);"),
    str: string_template("\tconst char* {0} = mp_obj_str_get_str({0}_obj);"),
    tuple: string_template(
        "\tmp_obj_t *{0} = NULL;\n\tsize_t {0}_len = 0;\n\tmp_obj_get_array({0}_arg, &{0}_len, &{0});"),
    list: string_template(
        "\tmp_obj_t *{0} = NULL;\n\tsize_t {0}_len = 0;\n\tmp_obj_get_array({0}_arg, &{0}_len, &{0});"),
    set: string_template(
        "\tmp_obj_t *{0} = NULL;\n\tsize_t {0}_len = 0;\n\tmp_obj_get_array({0}_arg, &{0}_len, &{0});"),
    object: string_template("\tmp_obj_t {0} args[ARG_{0}].u_obj;")
}


def stub_function(f):
    # Function implementation
    stub_ret = [function_comments(f), function_init(f"{f.__module__}_{f.__name__}")]
    sig = inspect.signature(f)
    stub_ret[-1] += function_params(sig.parameters)
    stub_ret.extend(parse_params(f, sig.parameters))
    ret_init = ret_val_init(sig.return_annotation)
    if ret_init:
        stub_ret.append(ret_init)
    stub_ret.append("")
    stub_ret.append(code(f))
    stub_ret.append("")
    stub_ret.append(ret_val_return(sig.return_annotation))
    stub_ret.append("}")
    # C Function Definition
    stub_ret.append(function_reference(f, f"{f.__module__}_{f.__name__}", sig.parameters))
    return "\n".join(expand_newlines(stub_ret))


def stub_module(mod):
    stub_ret = [headers()]
    classes = [o[1] for o in inspect.getmembers(mod) if inspect.isclass(o[1])]
    functions = [o[1] for cls in classes for o in inspect.getmembers(cls) if inspect.isfunction(o[1])]
    functions.extend([o[1] for o in inspect.getmembers(mod) if inspect.isfunction(o[1])])
    # Define the functions
    for func in functions:
        stub_ret.append(stub_function(func))
    # Set up the module properties
    stub_ret.append("")
    stub_ret.append(f"STATIC const mp_rom_map_elem_t {mod.__name__}_module_globals_table[] = {{")
    stub_ret.append(f"\t{{ MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) }},")
    stub_ret.extend(
        [f"\t{{ MP_ROM_QSTR(MP_QSTR_{f.__name__}), MP_ROM_PTR(&{mod.__name__}_{f.__name__}_obj) }}," for f in
         functions])
    stub_ret.append("};")
    stub_ret.append("")
    stub_ret.append(f"STATIC MP_DEFINE_CONST_DICT({mod.__name__}_module_globals, {mod.__name__}_module_globals_table);")
    # Define the module object
    stub_ret.append(f"const mp_obj_module_t {mod.__name__}_user_cmodule = {{")
    stub_ret.append(f"\t.base = {{&mp_type_module}},")
    stub_ret.append(f"\t.globals = (mp_obj_dict_t*)&{mod.__name__}_module_globals,")
    stub_ret.append("};")
    # Register the module
    stub_ret.append("")
    stub_ret.append(
        f"MP_REGISTER_MODULE(MP_QSTR_example, {mod.__name__}_user_cmodule, MODULE_{mod.__name__.upper()}_ENABLED);")
    return "\n".join(stub_ret)


def function_init(func_name):
    return f"STATIC mp_obj_t {func_name}("


return_type_handler = {
    int: "\tmp_int_t ret_val;",
    float: "\tmp_float_t ret_val;",
    bool: "\tbool ret_val;",
    str: "",
    # tuple: string_template(
    #     "\tmp_obj_t *{0} = NULL;\n\tsize_t {0}_len = 0;\n\tmp_obj_get_array({0}_arg, &{0}_len, &{0});"),
    # list: string_template(
    #     "\tmp_obj_t *{0} = NULL;\n\tsize_t {0}_len = 0;\n\tmp_obj_get_array({0}_arg, &{0}_len, &{0});"),
    # set: string_template(
    #     "\tmp_obj_t *{0} = NULL;\n\tsize_t {0}_len = 0;\n\tmp_obj_get_array({0}_arg, &{0}_len, &{0});"),
    None: ""
}

return_handler = {
    int: "\treturn mp_obj_new_int(ret_val);",
    float: "\treturn mp_obj_new_float(ret_val);",
    bool: "\treturn mp_obj_new_bool(ret_val);",
    str: "\treturn mp_obj_new_str(<ret_val_ptr>, <ret_val_len>);",
    None: "\treturn mp_const_none;"
}


def ret_val_init(ret_type):
    return return_type_handler[ret_type]


def ret_val_return(ret_type):
    return return_handler[ret_type]


def function_params(params):
    if len(params) == 0:
        return "() {"
    simple = all([param.kind == param.POSITIONAL_OR_KEYWORD for param in params.values()])
    if simple and len(params) < 4:
        params = ", ".join([f"mp_obj_t {x}_obj" for x in params])
        return params + ") {"
    elif simple:
        return "size_t n_args, const mp_obj_t *args) {"
    else:
        # Complex case
        return "size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {"


def kw_enum(params):
    return f"\tenum {{ {', '.join(['ARG_' + k for k in params])} }};"


shortened_types = {
    int: "int",
    object: "obj",
    None: "null",
    bool: "bool",
}


def kw_allowed_args(f, params):
    args = []
    for name, param in params.items():
        if param.kind in [param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY]:
            arg_type = "MP_ARG_REQUIRED"
        else:
            arg_type = "MP_ARG_KW_ONLY"
        type_txt = shortened_types[param.annotation]
        if param.default is inspect._empty:
            default = ""
        elif param.default is None:
            default = f"{{ .u_{type_txt} = MP_OBJ_NULL }}"
        else:
            default = f"{{ .u_{type_txt} = {param.default} }}"
        args.append(f"{{ MP_QSTR_{name}, {arg_type} | MP_ARG_{type_txt.upper()}, {default} }},")
    args = "\n\t\t".join(args)
    return f"\tSTATIC const mp_arg_t {f.__module__}_{f.__name__}_allowed_args[] = {{\n\t\t{args}\n\t}};"


def arg_array(f):
    args = f"{f.__module__}_{f.__name__}_allowed_args"
    return f"\tmp_arg_val_t args[MP_ARRAY_SIZE({args})];\n" \
        f"\tmp_arg_parse_all(n_args - 1, pos_args + 1, kw_args,\n" \
        f"\t\tMP_ARRAY_SIZE({args}), {args}, args);"


def arg_unpack(params):
    return "\n".join(
        f"\tmp_{shortened_types[param.annotation]}_t {name} = args[ARG_{name}].u_{shortened_types[param.annotation]};"
        for name, param in params.items())


def parse_params(f, params):
    """
    :param params: Parameter signature from inspect.signature
    :return: list of strings defining the parsed parameters in c
    """
    simple = all([param.kind == param.POSITIONAL_OR_KEYWORD for param in params.values()])
    if simple:
        return [type_handler[value.annotation](param) for param, value in params.items()]
    else:
        return [kw_enum(params), kw_allowed_args(f, params), "", arg_array(f), "", arg_unpack(params)]


def headers():
    return """// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
"""


def function_comments(f):
    """
    Uses single line comments as we can't know if there are string escapes such as /* in the code
    :param f:
    :return:
    """
    try:
        return '\n'.join(["//" + line.strip() for line in f.__doc__.splitlines()])
    except AttributeError:
        return "// No Comment"


def code(f):
    try:
        return f.code
    except AttributeError:
        return "\t//Your code here"


def function_reference(f, name, params):
    simple = all([param.kind == param.POSITIONAL_OR_KEYWORD for param in params.values()])
    if simple and len(params) < 4:
        return f"MP_DEFINE_CONST_FUN_OBJ_{len(params)}({name}_obj, {name});"
    elif simple:
        return f"MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN({name}_obj, {len(params)}, {len(params)}, {name});"
    else:
        return f"MP_DEFINE_CONST_FUN_OBJ_KW({f.__module__}_{f.__name__}_obj, 1, {f.__module__}_{f.__name__});"


def filter_comments(csvfile):
    for row in csvfile:
        if row.startswith('#'):
            continue
        yield row


def register_func(func_name, address, length, access_control, mod="csr"):
    def write_func(value: int) -> None:
        pass

    def read_func() -> int:
        pass

    write_func.__name__ = f"{func_name}_write"
    write_func.__qualname__ = f"{func_name}_write"
    write_func.__module__ = mod
    write_func.__doc__ = f"""writes a value to {func_name} @ register {address}"""
    write_func.code = f"\tret_val = {func_name}_read();"

    read_func.__name__ = f"{func_name}_read"
    read_func.__qualname__ = f"{func_name}_read"
    read_func.__doc__ = f""":return: value from {func_name} @ register {address}"""
    read_func.__module__ = mod
    read_func.code = f"\t{func_name}_write(value);"

    if access_control == "ro":
        return [read_func]
    elif access_control == "rw":
        return [read_func, write_func]


csr_types = {
    "csr_register": register_func
}


def parse_csv(path, module_name="csr"):
    mod = types.ModuleType(module_name)
    with open(path) as f:
        reader = csv.reader(filter_comments(f))
        for csr_type, func_name, address, length, access_control in reader:
            if csr_type in csr_types:
                funcs = csr_types[csr_type](func_name, address, length, access_control, mod)
                for func in funcs:
                    setattr(mod, func.__name__, func)
    return mod
