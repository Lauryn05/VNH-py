# python version 1.0                                            DO NOT EDIT
#
# Generated by smidump version 0.4.8:
#
#   smidump -f python DEMO-MIB

FILENAME = "DEMO-MIB.mib"

MIB = {
    "moduleName" : "DEMO-MIB",

    "DEMO-MIB" : {
        "nodetype" : "module",
        "language" : "SMIv2",
        "organization" :
            """Your Organization""",
        "contact" :
            """Your Contact Info""",
        "description" :
            """Demo MIB for testing""",
        "revisions" : (
            {
                "date" : "2024-06-16 00:00",
                "description" :
                    """[Revision added by libsmi due to a LAST-UPDATED clause.]""",
            },
        ),
        "identity node" : "demo",
    },

    "imports" : (
        {"module" : "SNMPv2-SMI", "name" : "MODULE-IDENTITY"},
        {"module" : "SNMPv2-SMI", "name" : "OBJECT-TYPE"},
        {"module" : "SNMPv2-SMI", "name" : "enterprises"},
        {"module" : "SNMPv2-SMI", "name" : "Counter32"},
        {"module" : "SNMPv2-SMI", "name" : "Gauge32"},
        {"module" : "SNMPv2-TC", "name" : "DisplayString"},
        {"module" : "SNMPv2-TC", "name" : "TimeStamp"},
    ),

    "nodes" : {
        "demo" : {
            "nodetype" : "node",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42",
            "status" : "current",
        }, # node
        "demoString" : {
            "nodetype" : "scalar",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.1",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-TC", "name" : "DisplayString"},
            },
            "access" : "readwrite",
            "description" :
                """A read-write object of type String.""",
        }, # scalar
        "demoInteger" : {
            "nodetype" : "scalar",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.2",
            "status" : "current",
            "syntax" : {
                "type" :                 {
                    "basetype" : "Enumeration",
                    "up" : {
                        "nodetype" : "namednumber",
                        "number" : "1"
                    },
                    "down" : {
                        "nodetype" : "namednumber",
                        "number" : "2"
                    },
                },
            },
            "access" : "readwrite",
            "description" :
                """A read-write object of type Integer.""",
        }, # scalar
        "demoOid" : {
            "nodetype" : "scalar",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.3",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"", "name" : "ObjectIdentifier"},
            },
            "access" : "readwrite",
            "description" :
                """A read-write object of type Oid.""",
        }, # scalar
        "demoTable" : {
            "nodetype" : "table",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.10",
            "status" : "current",
            "description" :
                """A table.""",
        }, # table
        "demoEntry" : {
            "nodetype" : "row",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.10.1",
            "status" : "current",
            "linkage" : [
                "demoEntryIndex",
            ],
            "description" :
                """An entry in the table demoTable.""",
        }, # row
        "demoEntryIndex" : {
            "nodetype" : "column",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.10.1.1",
            "status" : "current",
            "syntax" : {
                "type" :                 {
                    "basetype" : "Integer32",
                    "ranges" : [
                    {
                        "min" : "1",
                        "max" : "2147483647"
                    },
                    ],
                    "range" : {
                        "min" : "1",
                        "max" : "2147483647"
                    },
                },
            },
            "access" : "noaccess",
            "description" :
                """An index to uniquely identify the entry.""",
        }, # column
        "demoEntryString" : {
            "nodetype" : "column",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.10.1.2",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-TC", "name" : "DisplayString"},
            },
            "access" : "readwrite",
            "description" :
                """A read-write column of type String.""",
        }, # column
        "demoEntryInteger" : {
            "nodetype" : "column",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.10.1.3",
            "status" : "current",
            "syntax" : {
                "type" :                 {
                    "basetype" : "Enumeration",
                    "up" : {
                        "nodetype" : "namednumber",
                        "number" : "1"
                    },
                    "down" : {
                        "nodetype" : "namednumber",
                        "number" : "2"
                    },
                },
            },
            "access" : "readwrite",
            "description" :
                """A read-write column of type Integer.""",
        }, # column
        "demoEntryOid" : {
            "nodetype" : "column",
            "moduleName" : "DEMO-MIB",
            "oid" : "1.3.6.1.4.1.42.10.1.4",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"", "name" : "ObjectIdentifier"},
            },
            "access" : "readwrite",
            "description" :
                """A read-write column of type Oid.""",
        }, # column
    }, # nodes

}