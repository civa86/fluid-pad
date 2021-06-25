from fluid_pad.utils.singleton import Singleton


class DrumsService(metaclass=Singleton):
  a = 1

  def set_a(self, val):
    self.a = val
