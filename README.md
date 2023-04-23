# Practica2

El objetivo de esta práctica es implementar, mediante el uso de monitores, las diferentes funciones que vayan regulando el paso de coches y peatones por un puente. Es importante tener en cuenta que no puede haber simultáneamente en el puente coches con diferente dirección o peatones y coches.

Se han realizado dos versiones de esta práctica: 

- En la primera, más básica, nos hemos centrado en que se verifiquen las condiciones de seguridad. 

- En la segunda, además, hemos implementado un sistema de turnos para tratar con otros aspectos como la inanición.

Para verificar las variables condición hemos implementado funciones de forma que nos informen de si se cumplen los requisitos para que un objeto acceda al puente. Por ejemplo, para que un coche dirección sur pueda acceder debe cumplirse que sea el turno de esos coches y que además dentro del puente no haya ni coches con dirección norte ni peatones.
