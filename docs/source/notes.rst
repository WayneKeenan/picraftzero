=====
Notes
=====

.. currentmodule:: picraft

.. _keep-your-script-running:

Keep your script running
========================


The following file includes an  :func:`~picraft.zero.start()` to keep the
script alive::

    from picraft.zero import Joystick, Wheelbase, steering_mixer, start

    joystick= Joystick()
    wheelbase = Wheelbase(left=0, right=1)
    wheelbase.source = steering_mixer(joystick.values)

    start()