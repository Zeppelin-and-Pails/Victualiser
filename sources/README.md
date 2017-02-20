#sources

The data sources for victualiser to gather from.

Each source must have the following:
* a `victuals` module containing three classes
   * `Gatherer` implementing a `gather` method to collect data
   * `Chef` implementing a `cook` method to enrich the data
   * `Waiter` implementing a `serve` method to return the data to a consumer (preferably in either json or pandas form)
