import inspect


def stub(f):
    return """// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"

// This is the function which will be called from Python as example.add_ints(a, b).
STATIC mp_obj_t example_add_ints(mp_obj_t a_obj, mp_obj_t b_obj) {
    // Extract the ints from the micropython input objects
    int a = mp_obj_get_int(a_obj);
    int b = mp_obj_get_int(b_obj);

    // Calculate the addition and convert to MicroPython object.
    return mp_obj_new_int(a + b);
}
// Define a Python reference to the function above
STATIC MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);

// Define all properties of the example module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) },
    { MP_ROM_QSTR(MP_QSTR_add_ints), MP_ROM_PTR(&example_add_ints_obj) },
};
"""


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


def stub(f):
    stub_ret = []
    stub_ret.append(headers())
    stub_ret.append(function_comments(f))
    stub_ret.append(function_init(f.__name__))
    sig = inspect.signature(f)
    stub_ret.append(function_params(sig.parameters))
    stub_ret.extend(parse_params(sig.parameters))
    stub_ret.append(ret_val_init(sig.return_annotation))
    stub_ret.append(code())
    stub_ret.append(ret_val_return(sig.return_annotation))
    stub_ret.append("}")

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
        params = "\t" + ", ".join([f"mp_object {x}_obj" for x in params])
        return params + ") {"
    else:
        return "\tsize_t n_args, const mp_obj_t *args) {"


def parse_params(params):
    return [type_handler[value.annotation](param) for param, value in
            params.items()]


def headers():
    return """// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
"""


def function_comments(f):
    return "/*" + '\n'.join([line.strip() for line in f.__doc__.splitlines()]) + "/*"


def code():
    return "\n\t// your code here\n"


if __name__ == "__main__":
    def add_ints(a: int, b: str) -> int:
        """
        Adds two integers
        :param a:
        :param b:
        :return:
        """


    print(stub(add_ints))
