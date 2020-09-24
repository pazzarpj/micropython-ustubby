import ustubby


def test_basic_example():
    def add_ints(a: int, b: int) -> int:
        """Adds two integers
        :param a:
        :param b:
        :return:a + b"""

    add_ints.__module__ = "example"
    lines = """
//Adds two integers
//:param a:
//:param b:
//:return:a + b
STATIC mp_obj_t example_add_ints(mp_obj_t a_obj, mp_obj_t b_obj) {
    mp_int_t a = mp_obj_get_int(a_obj);
    mp_int_t b = mp_obj_get_int(b_obj);
    mp_int_t ret_val;

    //Your code here

    return mp_obj_new_int(ret_val);
}
MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);""".splitlines()

    call_lines = ustubby.stub_function(add_ints).splitlines()
    for index, line in enumerate(lines):
        assert call_lines[index] == line


def test_basic_example_load_function():
    def add_ints(a: int, b: int) -> int:
        """Adds two integers
        :param a:
        :param b:
        :return:a + b"""

    add_ints.__module__ = "example"
    func = ustubby.FunctionContainer().load_python(add_ints)
    assert func.to_c_comments() == """//Adds two integers\n//:param a:\n//:param b:\n//:return:a + b"""
    assert func.to_c_func_def() == "STATIC mp_obj_t example_add_ints"
    assert func.to_c_return_val_init() == "mp_int_t ret_val;"
    assert func.to_c_code_body() == "//Your code here"
    assert func.to_c_return_value() == "return mp_obj_new_int(ret_val);"
    assert func.to_c_define() == "MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);"
    assert func.to_c_arg_array_def() is None


def test_basic_example_load_function_e2e():
    def add_ints(a: int, b: int) -> int:
        """Adds two integers
        :param a:
        :param b:
        :return:a + b"""

    add_ints.__module__ = "example"
    lines = """//Adds two integers
//:param a:
//:param b:
//:return:a + b
STATIC mp_obj_t example_add_ints(mp_obj_t a_obj, mp_obj_t b_obj) {
    mp_int_t a = mp_obj_get_int(a_obj);
    mp_int_t b = mp_obj_get_int(b_obj);
    mp_int_t ret_val;

    //Your code here

    return mp_obj_new_int(ret_val);
}
MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);""".splitlines()
    func = ustubby.FunctionContainer().load_python(add_ints)
    print(func.to_c())
    call_lines = func.to_c().splitlines()
    for index, line in enumerate(lines):
        assert call_lines[index] == line


def test_readfrom_mem():
    def readfrom_mem(addr: int = 0, memaddr: int = 0, arg: object = None, *, addrsize: int = 8) -> str:
        """
        :param addr:
        :param memaddr:
        :param arg:
        :param addrsize:
        :return:
        """

    readfrom_mem.__module__ = "example"
    lines = """
//
//:param addr:
//:param memaddr:
//:param arg:
//:param addrsize:
//:return:
//
STATIC mp_obj_t example_readfrom_mem(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum { ARG_addr, ARG_memaddr, ARG_arg, ARG_addrsize };
    STATIC const mp_arg_t example_readfrom_mem_allowed_args[] = {
        { MP_QSTR_addr, MP_ARG_REQUIRED | MP_ARG_INT, { .u_int = 0 } },
        { MP_QSTR_memaddr, MP_ARG_REQUIRED | MP_ARG_INT, { .u_int = 0 } },
        { MP_QSTR_arg, MP_ARG_REQUIRED | MP_ARG_OBJ, { .u_obj = MP_OBJ_NULL } },
        { MP_QSTR_addrsize, MP_ARG_KW_ONLY | MP_ARG_INT, { .u_int = 8 } },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(example_readfrom_mem_allowed_args)];
    mp_arg_parse_all(n_args - 1, pos_args + 1, kw_args,
        MP_ARRAY_SIZE(example_readfrom_mem_allowed_args), example_readfrom_mem_allowed_args, args);

    mp_int_t addr = args[ARG_addr].u_int;
    mp_int_t memaddr = args[ARG_memaddr].u_int;
    mp_obj_t arg = args[ARG_arg].u_obj;
    mp_int_t addrsize = args[ARG_addrsize].u_int;

    //Your code here

    return mp_obj_new_str(<ret_val_ptr>, <ret_val_len>);
}
MP_DEFINE_CONST_FUN_OBJ_KW(example_readfrom_mem_obj, 1, example_readfrom_mem);""".splitlines()
    call_lines = ustubby.stub_function(readfrom_mem).splitlines()
    for index, line in enumerate(call_lines):
        assert line == lines[index]


def test_readfrom_mem_load_function():
    def readfrom_mem(addr: int = 0, memaddr: int = 0, arg: object = None, *, addrsize: int = 8) -> str:
        """
        :param addr:
        :param memaddr:
        :param arg:
        :param addrsize:
        :return:
        """

    readfrom_mem.__module__ = "example"
    func = ustubby.FunctionContainer().load_python(readfrom_mem)
    assert func.to_c_comments() == """//:param addr:\n//:param memaddr:\n//:param arg:\n//:param addrsize:\n//:return:"""
    assert func.to_c_func_def() == "STATIC mp_obj_t example_readfrom_mem"
    assert func.to_c_return_val_init() is None
    assert func.to_c_code_body() == "//Your code here"
    assert func.to_c_return_value() == "return mp_obj_new_str(<ret_val_ptr>, <ret_val_len>);"
    assert func.to_c_define() == "MP_DEFINE_CONST_FUN_OBJ_KW(example_readfrom_mem_obj, 1, example_readfrom_mem);"
    assert func.to_c_arg_array_def() == "STATIC const mp_arg_t example_readfrom_mem_allowed_args[]"


def test_many_positional_arguments():
    def MahonyAHRSupdate(gx: float, gy: float, gz: float, ax: float, ay: float, az: float, mx: float, my: float,
                         mz: float) -> None:
        """
        :param gx:
        :param gy:
        :param gz:
        :param ax:
        :param ay:
        :param az:
        :param mx:
        :param my:
        :param mz:
        :return:
        """

    MahonyAHRSupdate.__module__ = "MahonyAHRS"
    lines = """
//
//:param gx:
//:param gy:
//:param gz:
//:param ax:
//:param ay:
//:param az:
//:param mx:
//:param my:
//:param mz:
//:return:
//
STATIC mp_obj_t MahonyAHRS_MahonyAHRSupdate(size_t n_args, const mp_obj_t *args) {
    mp_float_t gx = mp_obj_get_float(args[0]);
    mp_float_t gy = mp_obj_get_float(args[1]);
    mp_float_t gz = mp_obj_get_float(args[2]);
    mp_float_t ax = mp_obj_get_float(args[3]);
    mp_float_t ay = mp_obj_get_float(args[4]);
    mp_float_t az = mp_obj_get_float(args[5]);
    mp_float_t mx = mp_obj_get_float(args[6]);
    mp_float_t my = mp_obj_get_float(args[7]);
    mp_float_t mz = mp_obj_get_float(args[8]);

    //Your code here

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(MahonyAHRS_MahonyAHRSupdate_obj, 9, 9, MahonyAHRS_MahonyAHRSupdate);""".splitlines()
    call_lines = ustubby.stub_function(MahonyAHRSupdate).splitlines()
    for index, line in enumerate(call_lines):
        assert line == lines[index]


def test_many_positional_arguments_function():
    def MahonyAHRSupdate(gx: float, gy: float, gz: float, ax: float, ay: float, az: float, mx: float, my: float,
                         mz: float) -> None:
        """
        :param gx:
        :param gy:
        :param gz:
        :param ax:
        :param ay:
        :param az:
        :param mx:
        :param my:
        :param mz:
        :return:
        """

    MahonyAHRSupdate.__module__ = "MahonyAHRS"
    lines = """//:param gx:
//:param gy:
//:param gz:
//:param ax:
//:param ay:
//:param az:
//:param mx:
//:param my:
//:param mz:
//:return:
STATIC mp_obj_t MahonyAHRS_MahonyAHRSupdate(size_t n_args, const mp_obj_t *args) {
    mp_float_t gx = mp_obj_get_float(args[0]);
    mp_float_t gy = mp_obj_get_float(args[1]);
    mp_float_t gz = mp_obj_get_float(args[2]);
    mp_float_t ax = mp_obj_get_float(args[3]);
    mp_float_t ay = mp_obj_get_float(args[4]);
    mp_float_t az = mp_obj_get_float(args[5]);
    mp_float_t mx = mp_obj_get_float(args[6]);
    mp_float_t my = mp_obj_get_float(args[7]);
    mp_float_t mz = mp_obj_get_float(args[8]);

    //Your code here

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(MahonyAHRS_MahonyAHRSupdate_obj, 9, 9, MahonyAHRS_MahonyAHRSupdate);""".splitlines()
    func = ustubby.FunctionContainer().load_python(MahonyAHRSupdate)
    call_lines = func.to_c().splitlines()
    for index, line in enumerate(lines):
        assert call_lines[index] == line

def test_module_comments_no_comment(mocker):
    mocker.patch("ustubby.__doc__", None)
    docs = ustubby.module_doc(ustubby)
    assert docs == """/*This file was auto-generated using uStubby.
https://github.com/pazzarpj/micropython-ustubby
*/"""

def test_module_comments_with_comment(mocker):
    mocker.patch("ustubby.__doc__", """Multi
line
comments
""")
    docs = ustubby.module_doc(ustubby)
    assert docs == """/*This file was auto-generated using uStubby.
https://github.com/pazzarpj/micropython-ustubby

Multi
line
comments

*/"""
