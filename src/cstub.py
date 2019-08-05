import inspect


def string_template(base_str):
    def string_handle(*args, **kwargs):
        return base_str.format(*args, **kwargs)

    return string_handle


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
}


def stub_function(f):
    # Function implementation
    stub_ret = [function_comments(f), function_init(f"{f.__module__}_{f.__name__}")]
    sig = inspect.signature(f)
    stub_ret[-1] += function_params(sig.parameters)
    stub_ret.extend(parse_params(sig.parameters))
    stub_ret.append(ret_val_init(sig.return_annotation))
    stub_ret.append(code())
    stub_ret.append(ret_val_return(sig.return_annotation))
    stub_ret.append("}")
    # C Function Definition
    stub_ret.append(function_reference(f"{f.__module__}_{f.__name__}", sig.parameters))
    return stub_ret


def stub_module(mod):
    stub_ret = [headers()]
    functions = [o[1] for o in inspect.getmembers(mod) if inspect.isfunction(o[1])]
    # Define the functions
    for func in functions:
        stub_ret.extend(stub_function(func))
    # Set up the module properties
    stub_ret.append(f"STATIC const mp_rom_map_elem_t {mod.__name__}_module_globals_table[] = {{")
    stub_ret.append(f"\t{{ MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) }},")
    stub_ret.extend(
        [f"\t{{ MP_ROM_QSTR(MP_QSTR_{f.__name__}), MP_ROM_PTR(&{mod.__name__}_{f.__name__}_obj) }}," for f in
         functions])
    stub_ret.append("};")
    stub_ret.append(f"STATIC MP_DEFINE_CONST_DICT({mod.__name__}_module_globals, {mod.__name__}_module_globals_table);")
    # Define the module object
    stub_ret.append(f"const mp_obj_module_t {mod.__name__}user_cmodule = {{")
    stub_ret.append(f"\t.base = {{&mp_type_module}},")
    stub_ret.append(f"\t.globals = (mp_obj_dict_t*)&{mod.__name__}_module_globals,")
    stub_ret.append("};")
    # Register the module
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
    str: "\treturn mp_obj_new_str({ret_val_ptr}, {ret_val_len})",
    None: "\treturn mp_const_none;"
}


def ret_val_init(ret_type):
    return return_type_handler[ret_type]


def ret_val_return(ret_type):
    return return_handler[ret_type]


def function_params(params):
    if len(params) == 0:
        return "() {"
    if len(params) < 4:
        params = ", ".join([f"mp_object {x}_obj" for x in params])
        return params + ") {"
    else:
        return "size_t n_args, const mp_obj_t *args) {"


def parse_params(params):
    return [type_handler[value.annotation](param) for param, value in params.items()]


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
    return '\n'.join(["//" + line.strip() for line in f.__doc__.splitlines()])


def code():
    return "\n\t// your code here\n"


def function_reference(name, params):
    if len(params) < 4:
        return f"MP_DEFINE_CONST_FUN_OBJ_{len(params)}({name}_obj, {name});"
    else:
        return f"MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN({name}_obj, {len(params)}, {len(params)}, {name});"


if __name__ == "__main__":
    import example

    # def add_ints(a: int, b: str, c: float, d: tuple) -> int:
    #     """
    #     Adds two integers
    #     :param a:
    #     :param b:
    #     :return:
    #     """

    # print("\n".join(stub_function(example.add_ints)))
    print(stub_module(example))
