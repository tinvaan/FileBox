
class Env:
    @classmethod
    def load(cls, ctx):
        return cls(ctx)

    def __init__(self, ctx):
        self.host = 'http://%s:%s' % (ctx.get('FILEBOX_SERVER'),
                                      ctx.get('FILEBOX_PORT'))