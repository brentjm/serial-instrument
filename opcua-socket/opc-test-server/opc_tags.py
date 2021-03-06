from opcua import ua

tags_dict = {'CONFIG_NAME_DLV':
    {
        'tag_type':ua.ObjectIds.String,
        'tag_writable':False,
        'tag_init':''
    },
    'CONFIG_NAME_PAT':
    {
        'tag_type':ua.ObjectIds.String,
        'tag_writable':True,
        'tag_init':''
    },
    'STRING1_DLV':
    {
        'tag_type':ua.ObjectIds.String,
        'tag_writable':False,
        'tag_init':''
    },
    'STRING1_PAT':
    {
        'tag_type':ua.ObjectIds.String,
        'tag_writable':True,
        'tag_init':''
    },
    'INT1_PAT':
    {
        'tag_type':ua.ObjectIds.Int16,
        'tag_writable':True,
        'tag_init':0
    },
    'FLOAT1_PAT':
    {
        'tag_type':ua.ObjectIds.Float,
        'tag_writable':True,
        'tag_init':0
    }
}
