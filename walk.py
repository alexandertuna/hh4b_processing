def walk(top):
    """
    os.path.walk like function for TDirectories.
    Return 4-tuple: (dirpath, dirnames, filenames, top)
    """
    import ROOT
    assert isinstance(top, ROOT.TDirectory)

    names     = [k.GetName() for k in top.GetListOfKeys()]
    dirnames  = []
    filenames = []

    for name in names:
        dir = top.Get(name)
        if isinstance(dir, ROOT.TDirectory):
            dirnames.append(name)
        else:
            filenames.append(name)

    dirnames.sort()
    filenames.sort()

    yield top.GetPath(), dirnames, filenames, top

    for dirname in dirnames:
        dir = top.Get(dirname)
        for x in walk(dir):
            yield x


