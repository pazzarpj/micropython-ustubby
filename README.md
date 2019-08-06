# uStubby

uStubby is a library for generating micropython c extension stubs from type annotated python.

According to [Link](https://micropython.org/)

"MicroPython is a lean and efficient implementation of the Python 3 programming language that includes a small subset of the Python standard library and is optimised to run on microcontrollers and in constrained environments."

Sometimes, pure python performance isn't enough.
C extensions are a way to improve performace whilst still having the bulk of your code in micropython.

Unfortunately there is a lot of boilerplate code needed to build these extensions. 

uStubby is designed to make this process as easy as writing python.

## Getting Started

uStubby is targeted to run on Python 3.7, but should run on versions 3.6 or greater

### Installing

Currently, there are no external dependencies for running uStubby.
Clone the repository using git and just put it on the path to install.
Alternatively, install from PyPI with 
```bash
pip install ustubby
```

## Usage
This example follows generating the template as shown [here](http://docs.micropython.org/en/latest/develop/cmodules.html#basic-example)

Create a python file with the module as you intend to use it from micropython.

eg. example.py
```python
def add_ints(a: int, b: int) -> int:
    """Adds two integers
    :param a:
    :param b:
    :return:a + b"""
```
We can then convert this into the appropriate c stub by running
```python
import ustubby
import example

print(ustubby.stub_module(example))
```
<details><summary>Output</summary><p>

```c
// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"

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
MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);

STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
	{ MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) },
	{ MP_ROM_QSTR(MP_QSTR_add_ints), MP_ROM_PTR(&example_add_ints_obj) },
};

STATIC MP_DEFINE_CONST_DICT(example_module_globals, example_module_globals_table);
const mp_obj_module_t example_user_cmodule = {
	.base = {&mp_type_module},
	.globals = (mp_obj_dict_t*)&example_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_example, example_user_cmodule, MODULE_EXAMPLE_ENABLED);
```
</p></details>

This will parse all the functions in the module and attach them to the same namespace in micropython.
##### Note: It will only generate the boilerplate code and not the actual code that does the work such as a + b
After editing the code in the template at the place marked //Code goes here you can follow the instructions 
[here](http://docs.micropython.org/en/latest/develop/cmodules.html#basic-example) for modifying 
the Make File and building the module into your micro python deployment.

You should then be able to use the module in micro python by typing
```python
import example # from example.c compiled into micropython
example.add_ints(1, 2)
# prints 3
```
##### Note: This example.py is the one compiled into the micropython source and not the file we created earlier

### Advanced usage
If you added two more functions to the original example.py
```python
def lots_of_parameters(a: int, b: float, c: tuple, d: object, e: str) -> None:
    """
    :param a:
    :param b:
    :param c:
    :param d:
    :return:
    """

def readfrom_mem(addr: int = 0, memaddr: int = 0, arg: object = None, *, addrsize: int = 8) -> str:
    """
    :param addr:
    :param memaddr:
    :param arg:
    :param addrsize: Keyword only arg
    :return:
    """
```

logs_of_parameters shows the types of types you can parse in. You always need to annotate each parameter and the return.
readfrom_mem shows that you can set default values for certain parameters and specify that addrsize is a keyword only
argument.

At the c level in micropython, there is only three ways of implementing a function.
##### Basic Case
```python
def foo(a, b, c): # 0 to 3 args
    pass
```
```c
MP_DEFINE_CONST_FUN_OBJ_X // Where x is 0 to 3 args
```
##### Greater than three positional args
```python
def foo(*args):
    pass
```
```c
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN
```
##### Arbitary args
```python
def foo(*args, **kwargs):
    pass
```
```c
MP_DEFINE_CONST_FUN_OBJ_KW
```
Each successively increasing the boiler plate to conveniently accessing the variables.
Using the same code to parse it
```python
import ustubby
import example

print(ustubby.stub_module(example))
```
<details><summary>Output</summary><p>

```c
// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"

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
MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);
//
//:param a:
//:param b:
//:param c:
//:param d:
//:return:
//
STATIC mp_obj_t example_lots_of_parameters(size_t n_args, const mp_obj_t *args) {
    mp_int_t a = mp_obj_get_int(a_obj);
    mp_float_t b = mp_obj_get_float(b_obj);
    mp_obj_t *c = NULL;
    size_t c_len = 0;
    mp_obj_get_array(c_arg, &c_len, &c);
    mp_obj_t d args[ARG_d].u_obj;

    //Your code here

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(example_lots_of_parameters_obj, 4, 4, example_lots_of_parameters);
//
//:param addr:
//:param memaddr:
//:param arg:
//:param addrsize: Keyword only arg
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
MP_DEFINE_CONST_FUN_OBJ_KW(example_readfrom_mem_obj, 1, example_readfrom_mem);

STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
	{ MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) },
	{ MP_ROM_QSTR(MP_QSTR_add_ints), MP_ROM_PTR(&example_add_ints_obj) },
	{ MP_ROM_QSTR(MP_QSTR_lots_of_parameters), MP_ROM_PTR(&example_lots_of_parameters_obj) },
	{ MP_ROM_QSTR(MP_QSTR_readfrom_mem), MP_ROM_PTR(&example_readfrom_mem_obj) },
};

STATIC MP_DEFINE_CONST_DICT(example_module_globals, example_module_globals_table);
const mp_obj_module_t example_user_cmodule = {
	.base = {&mp_type_module},
	.globals = (mp_obj_dict_t*)&example_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_example, example_user_cmodule, MODULE_EXAMPLE_ENABLED);
```
</p></details>

#### Adding fully implemented c functions
Going one step further you can directly add c code to be substituted into the c generated code where the 
"//Your code here comment" is.

For example, starting with a fresh example.py you could define it as.

```python
def add_ints(a: int, b: int) -> int:
    """Adds two integers
    :param a:
    :param b:
    :return:a + b"""
add_ints.code = "    ret_val = a + b;"
```
to get a fully defined function in c

<details><summary>Output</summary><p>

```c
// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"

//Adds two integers
//:param a:
//:param b:
//:return:a + b
STATIC mp_obj_t example_add_ints(mp_obj_t a_obj, mp_obj_t b_obj) {
    mp_int_t a = mp_obj_get_int(a_obj);
    mp_int_t b = mp_obj_get_int(b_obj);
    mp_int_t ret_val;

    ret_val = a + b;

    return mp_obj_new_int(ret_val);
}
MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);

STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
	{ MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) },
	{ MP_ROM_QSTR(MP_QSTR_add_ints), MP_ROM_PTR(&example_add_ints_obj) },
};

STATIC MP_DEFINE_CONST_DICT(example_module_globals, example_module_globals_table);
const mp_obj_module_t example_user_cmodule = {
	.base = {&mp_type_module},
	.globals = (mp_obj_dict_t*)&example_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_example, example_user_cmodule, MODULE_EXAMPLE_ENABLED);
```
</p></details>

#### Using functions without a module definition
If you don't need the fully module boiler plate, you can generate individual functions with
```python
import ustubby
def add_ints(a: int, b: int) -> int:
    """add two ints"""
add_ints.code = "    ret_val = a + b;"
add_ints.__module__ = "new_module"

print(ustubby.stub_function(add_ints))
```

```c
//add two ints
STATIC mp_obj_t new_module_add_ints(mp_obj_t a_obj, mp_obj_t b_obj) {
    mp_int_t a = mp_obj_get_int(a_obj);
    mp_int_t b = mp_obj_get_int(b_obj);
    mp_int_t ret_val;

    ret_val = a + b;

    return mp_obj_new_int(ret_val);
}
MP_DEFINE_CONST_FUN_OBJ_2(new_module_add_ints_obj, new_module_add_ints);
```

#### Parsing Litex Files
uStubby is also trying to support c code generation from Litex files such as
```csv
#--------------------------------------------------------------------------------
# Auto-generated by Migen (5585912) & LiteX (e637aa65) on 2019-08-04 03:04:29
#--------------------------------------------------------------------------------
csr_register,cas_leds_out,0x82000800,1,rw
csr_register,cas_buttons_ev_status,0x82000804,1,rw
csr_register,cas_buttons_ev_pending,0x82000808,1,rw
csr_register,cas_buttons_ev_enable,0x8200080c,1,rw
csr_register,ctrl_reset,0x82001000,1,rw
csr_register,ctrl_scratch,0x82001004,4,rw
csr_register,ctrl_bus_errors,0x82001014,4,ro
```
Currently only csr_register is supported. Please raise issues if you need to expand this feature.
```python
import ustubby
mod = ustubby.parse_csv("csr.csv")
print(ustubby.stub_module(mod))
```

## Running the tests
Install the test requirements with 
```bash
pip install -r requirements-test.txt
```

## Check out the docs

TBD

## Contributing

Contributions are welcome. Get in touch or create a new pull request.

## Credits
Inspired by 
- [Extending MicroPython: Using C for Good](https://youtu.be/fUb3Urw4H-E)
- [Online C Stub Generator](https://gitlab.com/oliver.robson/mpy-c-stub-gen)
- [Micropython](https://micropython.org) 

PyCon AU 2019 Sprints

## Authors

* **Ryan Parry-Jones** - *Original Developer* - [pazzarpj](https://github.com/pazzarpj)

See also the list of [contributors](https://github.com/pazzarpj/micropython-ustubby/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details
