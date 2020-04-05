# A couple notes about the tests

## 1. The unit tests in this folder aren't really unit tests
The reason for this is that pretty much every method and function in `feupy` relies on sigarra (as you would expect). I could mock the cache with prefetched urls. However, two problems arise:

1. In order to test functions that need priviledged access to sigarra, i.e. functions that take a `Credentials` object as an argument, I would need to to store non-public sigarra pages.

2. What happens if a sigarra update changes the html of the pages but I forget to update the test urls? One can easily end in the situation that all the tests pass but `feupy` fails in the real world.

Long story short, the tests in this folder are more like integration tests (with sigarra) and they make web requests in order to make sure that the tests fail if sigarra changed the html layouts.

## 2. `FeupyTestCase` is `unittest.TestCase` plus a few utility methods

## 3. There will be a test file per `feupy` module
The test filenames are written in [camelCase](https://en.wikipedia.org/wiki/Camel_case "Camel case wikipedia page").