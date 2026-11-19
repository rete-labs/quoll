## Rules

```
  ensures:
    own surface          the root's [model.kernel.default interface] includes no part's [interface]

    layout alone         [layout] [uses] no [interface]
    model alone          [model] [uses] no [interface]

    grammar on layout    [grammar] [uses] [layout.default] alone

    source on three      [source] [uses] [layout.default], [grammar.default], [model.kernel],
                         [model.graph], [model.rich], [model.profile] and [model.generation] alone
    principles on model  [principles] [uses] [model.kernel], [model.graph], [model.rich],
                         [model.profile] and [model.generation] alone
```
