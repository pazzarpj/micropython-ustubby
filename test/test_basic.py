import ustubby


def test_basic_example():
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

    call_lines = ustubby.stub_function(add_ints)
    for index, line in enumerate(call_lines):
        assert line == lines[index]


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
    lines = """//
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
    call_lines = ustubby.stub_function(readfrom_mem)
    for index, line in enumerate(call_lines):
        assert line == lines[index]
