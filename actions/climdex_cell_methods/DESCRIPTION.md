# Cell methods for precipitation extremes

A collection of .yaml files used to set cell-methods on climdex indices, if one failed to notice that they are missing cell methods before one generates climatologies and adds them after the fact. That is, they all include the "time: mean over years" entry representing the climatology-generating process.

Note that these are different from the cell_method values already in the database:

| index         | old cell_method                    | new cell_method                                  |
|---------------|------------------------------------|--------------------------------------------------|
| cwdETCCDI     | time: maximum time: mean over days | time: maximum within years time: mean over years |
| idETCCDI      | time: maximum time: mean over days | time: sum within years time: mean over years     |
| prcptotETCCDI | time: maximum time: mean over days | time: sum within years time: mean over years     |
| r10mmETCCDI   | time: maximum time: mean over days | time: sum within years time: mean over years     |
| r20mmETCCDI   | time: maximum time: mean over days | time: sum within years time: mean over years     |
| r95pETCCDI    | time: maximum time: mean over days | time: sum within years time: mean over years     |
| r99pETCCDI    | time: maximum time: mean over days | time:sum within years time: mean over years      |
| rx1dayETCCDI  | time: maximum time: mean over days | time: maximum within years time: mean over years |
| rx5dayETCCDI  | time: maximum time: mean over days | time: maximum within years time: mean over years |
| sdiiETCCDI    | time: maximum time: mean over days | time: mean within years time: mean over years    |

Previously, all climdex indices had the cell method `time: maximum`.

It does not break anything in PCEX to provide different cell methods for newly added datasets, even though [we have not yet standardized all existing cell_methods values.](https://github.com/pacificclimate/climate-explorer-data-prep/issues/64) I have endeavoured to provide correct ones.