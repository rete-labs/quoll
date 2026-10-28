## Rules

```
  ensures:
    own surface          the root provides its [model.default interface] alone, which includes
                         no part's [model.interface]
    layout alone         [layout] [model.uses] no [model.interface]
    model alone          [model] [model.uses] no [model.interface]
    grammar on layout    [grammar] [model.uses] the [model.interface]s of [layout] alone
    source on three      [source] [model.uses] the [model.interface]s of [layout], [grammar] and
                         [model] alone
    principles on model  [principles] [model.uses] the [model.interface]s of [model] alone
```
