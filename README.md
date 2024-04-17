# Salt2Type: Saltarelle to TypeScript Migration Tool

## Introduction

[Script#](https://github.com/NikhilK/scriptsharp) is a language (a subset of C#) that, along with its associated compiler (Saltarelle) allows you to maintain your client-side code in C# and deploy it as JavaScript. This allows you to leverage existing C# code and enjoy all the development-side benefits of C# and the Visual Studio ecosystem (i.e. strong typing, complete IDE support, integrated unit testing, etc) - features which were not otherwise available when Script# was introduced in 2012.

Saltarelle also allows you to directly share .cs files between Script# and C# projects in order to maintain a common set of utilities/interfaces/etc across both codebases. This prevents the duplicate work of reimplementing the same business logic in both JavaScript and C# and maintains common strongly-typed interfaces across both sides. The original Saltarelle project was acquired by [Bridge.NET](https://github.com/bridgedotnet) in 2015 and discontinued in favor of their existing product which was not backwards compatible. More recently, the Bridge.NET project announced it too has shut down.

This project aims to provide tools to assist in migrating an existing codebase from Saltarelle to TypeScript.

## Modern Alternatives

If you are starting a new project from scratch, you should definitely not be building it on top of Script#. If you were considering reaching for Script#, you were probably trying to solve one of the following problems...

### Strongly-Typed Client Code and IDE Support

Strong typing eliminates certain classes of bugs from your programs and makes some aspects of maintaining and debugging code simpler. Since JavaScript is not a strongly typed language, there have been many different attempts to add typing to JavaScript over the years ([Flow](https://flow.org/), [JS++](https://www.onux.com/jspp/), [PureScript](https://www.purescript.org/), etc, etc, etc).

As of today, [TypeScript](https://www.typescriptlang.org/) is the most popular option for adding strong typing to JavaScript. It has excellent library and IDE support and has the backing of Microsoft. If all you are loking for is strong typing and good IDE support for your client-side code, this is all you need.

### Shared Client-Side and Server-Side Logic

It is common to have business logic which must be run on both the server-side and on the client-side of an application and be kept consistent across both (e.g. calculating whether a user has permission to perform an operation in order to show/hide the appropriate control on the client side; then also calculating it separately on the server side in order to enforce that a user is not able to bypass the client-side check). If you are using a different programming language on the server-side vs the client-side, you will need to reimplement your logic twice and make sure to keep those implementations consistent over time.

Today, you can run JavaScript/TypeScript code on the server side using [NodeJS](https://nodejs.org/en/). You can also run C# code on the client-side using [Blazor](https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor), which compiles C# code into WebAssembly. If all you are looking for is to write logic once and have it able to run in both places, you have the option of writing it either in JavaScript/TypeScript or in C# using either of these tools.

_If you need/wish to write your client-side primarily in TypeScript and your server-side primarily in C# and still share logic between them, take a look at [nuget-npm-crossdeployment](https://github.com/pangaeatech/nuget%5Fnpm%5Fcrossdeployment)._

### Shared Client-Side and Server-Side Typing

Most applications share objects between the server-side and client-side code and send objects back and forth using serialization (e.g. [JSON](https://www.json.org/json-en.html)). If you are using strong typing on both the client-side and server-side, you need to keep the type information consistent between both. If you are using the same language on both the server-side and client-side (such as using NodeJS or Blazor as discussed above), then this is not a problem.

However, if you need/wish to write your client-side code in TypeScript and your server-side code in C#, then the best approach is to have your C# server-side code generate an OpenAPI document detailing your types (using a tool such as [SwaggerGen](https://www.nuget.org/packages/Swashbuckle.AspNetCore.SwaggerGen/)) and then convert that into a TypeScript file using a tool such as [openapi-typescript](https://www.npmjs.com/package/openapi-typescript).

## Usage

### To migrate an existing Script# project to TypeScript:

1. Build the Script# project using Saltarelle in Debug mode:
   - `MSBuild.exe Project.csproj /p:Configuration=Debug`
2. Build XML documentation for the Script# project using Doxygen:
   - Copy `Doxyfile` from salt2type into your project's directory
   - `Doxygen Doxyfile`
   - `cd xml && xsltproc combine.xslt index.xml > all.xml`
3. Run `salt2type JSFILE XMLFILE OUTDIR NSNAME [IGNFILE]` where:
   - `JSFILE` = The (unminified) javascript file generated by Saltarelle
   - `XMLFILE` = The `all.xml` file generated by Doxygen
     - Optionally, you can specify "any" or "unknown" instead of a filename which will assign EVERYTHING to that type instead of pulling types from Doxygen
   - `OUTDIR` = The folder to populate with the new typescript project
   - `NSNAME` = The namespace to export for external use
   - `IGNFILE` = An optional file listing those classes, methods/properties to ignore
     - Classes are specified with their namespace (e.g. `package.subpackage.ClassName`)
     - Methods/Properties are specified with thir classes (e.g. `package.subpackage.ClassName:MethodName`)
4. Run the following commands in the newly created OUTDIR (fixing warnings and errors as you go):
   - `npm install`
   - `npm run format:fix`
   - `npm run lint:fix`
   - `npm run typecheck`
   - `npm run build`

### Tested Versions

- Doxygen 1.8.17
- MSBuild 14.0
- nodejs 16.19.1
- npm 8.1.0
- Python 3.8.10
- Saltarelle.Compiler 2.7.0
- xsltproc 1.1.34

### Limitations

This code only supports the subset of Script# that we needed to migrate our own legacy codebases. It does not support all possible Script# codebases. If the TypeScript implementations in `tpl/ss` do not include something you need, you can pull in additional functionality from [the Saltarelle Project](https://github.com/Saltarelle/SaltarelleCompiler/tree/develop/Runtime/CoreLib.Script/).

Typescript is fundamentally a compile-time typing system while Script# is a run-time typing system. Therefore, run-time type checking will _never_ be supported by `salt2type`. If your Script# codebase relies heavily on run-time type-checking (e.g. reflection), then you will need to refactor your existing Script# codebase prior to using `salt2type` to migrate it.

This code intentionally migrates away from custom implementations of classes which are now supported natively in TypeScript (e.g. `Record<K,V>` instead of `Dictionary<K,V>`) and away from polyfills for old browser support. If you need old browser support, you should consider using a library such as `es6-shim` or a service such as [polyfill.io](http://cdn.polyfill.io).
