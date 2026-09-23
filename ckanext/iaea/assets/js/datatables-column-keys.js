/*
 * DataTables reads a column's `data` option as an object path, so a datastore
 * column named e.g. "Sample No." or "Temperature [C]" is looked up as
 * row["Sample No"][""] / an array, and renders empty. Core datatablesview.js
 * passes the raw column id as `data`, so replace those accessors with plain
 * property lookups before the first draw.
 */
$(document).on('preInit.dt', function (_event, settings) {
  var getObjectDataFn = $.fn.dataTable.ext.internal._fnGetObjectDataFn

  settings.aoColumns.forEach(function (col) {
    var key = col.mData
    if (typeof key !== 'string' || !/[.[(]/.test(key)) {
      return
    }
    var mRender = col.mRender ? getObjectDataFn(col.mRender) : null

    col.fnGetData = function (rowData, type, meta) {
      var value = rowData[key]
      return mRender && type ? mRender(value, type, rowData, meta) : value
    }
    col.fnSetData = function (rowData, val) {
      rowData[key] = val
    }
  })
})
