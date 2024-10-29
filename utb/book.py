
class Chapter:

    def __init__(self, name, parent, content=[], index=0):
        self.name = name
        self.chapter = parent if isinstance(parent, Chapter) else None
        self.book = self.chapter.book if self.chapter else parent
        self.content = content
        self.index = index

    def __str__(self):
        parent = str(self.chapter) if self.chapter else str(self.book)
        name = (('%d. ' % self.index) if self.index else '') + self.name
        name = name[:19] + '…' if len(name) >= 20 else name
        return '%s > %s' % (parent, name)

    def get_problems(self):
        problems = []
        for obj in self.content:
            if isinstance(obj, Chapter):
                problems += obj.get_problems()
            else:
                problems.append(obj)
        return problems

    @classmethod
    def parse(cls, parent, data, index=0):
        if isinstance(data, (list, tuple)):
            chapter = cls(data[0], parent, data[1:])
        else:
            assert 'title' in data and 'arr' in data
            chapter = cls(data['title'], parent, index=index)
            for obj in data['arr']:
                chapter.content.append(cls.parse(chapter, obj))
        return chapter


class Book:

    def __init__(self, number):
        self.number = number
        self.content = []

    def __str__(self):
        return 'Book %d' % self.number

    def get_problems(self):
        problems = []
        for chapter in self.content:
            problems += chapter.get_problems()
        return problems

    @classmethod
    def parse(cls, number, data):
        book = cls(number)
        for index, obj in enumerate(data):
            book.content.append(Chapter.parse(book, obj, index + 1))
