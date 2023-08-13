def months_pl_shorts(month):
    pl_month = {
        'Jan': 'Sty',
        'Feb': 'Lut',
        'Mar': 'Mar',
        'Apr': 'Kwi',
        'May': 'Maj',
        'Jun': 'Cze',
        'Jul': 'Lip',
        'Aug': 'Sie',
        'Sep': 'Wrz',
        'Oct': 'Paź',
        'Nov': 'Lis',
        'Dec': 'Gru',
    }

    month_ = month[:2] + ' ' + pl_month[month[2:-4].strip()] + ' ' + month[-4:]

    return month_