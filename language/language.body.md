## Rules

```
  ensures:
    own surface          the root's [model.default interface] includes no part's [model.interface]
    layout alone         the [model.module] providing [layout.default] [model.uses] no
                         [model.interface]
    model alone          the [model.module] providing [model.default] [model.uses] no
                         [model.interface]
    grammar on layout    the [model.module] providing [grammar.default] [model.uses] the
                         [model.interface]s of the [model.module] providing [layout.default] alone
    source on three      the [model.module] providing [source.default] [model.uses] the
                         [model.interface]s of the [model.module]s providing [layout.default],
                         [grammar.default] and [model.default] alone
    principles on model  the [model.module] providing [principles.default] [model.uses] the
                         [model.interface]s of the [model.module] providing [model.default] alone
```
