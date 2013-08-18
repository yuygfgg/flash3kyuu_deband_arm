import re

import waflib

APPNAME = "flash3kyuu_deband"
VERSION = "2.0pre"

top = "."


def options(opt):
    opt.load("compiler_cxx")


def _check_cxx(conf, feature, fragment, mandatory=False):
    conf.check_cxx(
        msg=" - " + feature,
        define_name="HAVE_" + feature.replace(" ", "_").upper(),
        fragment=fragment,
        mandatory=mandatory,
    )


def configure(conf):
    def add_options(flags, options):
        for flag in flags:
            conf.env.append_unique(flag, options)

    conf.load("compiler_cxx")
    add_options(["CFLAGS", "CXXFLAGS"], ["-fPIC", "-mavx"])
    add_options(["CFLAGS", "CXXFLAGS"], ["-Werror", "-std=c++11"])
    _check_cxx(
        conf,
        "alignas",
        "int main() { alignas(8) int x = 0; return x; }",
        mandatory=True,
    )

    conf.find_program("python3", var="PYTHON3")


def build(bld):
    gen_output = bld.cmd_and_log(
        [bld.env["PYTHON3"], "gen_filter_def.py", "--list-outputs"],
        quiet=waflib.Context.BOTH,
    )
    gen_output_list = re.split(r"\s+", gen_output.strip(), flags=re.S)

    bld(
        rule="${PYTHON3} ${SRC[0].abspath()}",
        source="gen_filter_def.py",
        target=map(bld.path.find_node, gen_output_list),
        cwd=bld.path.abspath(),
    )
    bld(
        features="cxx",
        source=bld.path.ant_glob(
            "*.cpp",
            excl=[
                "dllmain.cpp",
                "icc_override.cpp",
                "stdafx.cpp",
                "debug_dump.cpp",
            ],
        ),
        target="objs",
    )
