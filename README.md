# Salt2Type: Saltarelle to TypeScript Migration Tool #

## Introduction

[Script#](https://github.com/NikhilK/scriptsharp) is a language (a subset of C#) that, along with its associated compiler (Saltarelle) allows you to maintain your client-side code in C# and deploy it as JavaScript.  This allows you to leverage existing C# code and enjoy all the development-side benefits of C# and the Visual Studio ecosystem (i.e. strong typing, complete IDE support, integrated unit testing, etc) - features which were not otherwise available when Script# was introduced in 2012.  

Saltarelle also allows you to directly share .cs files between Script# and C# projects in order to maintain a common set of utilities/interfaces/etc across both codebases.  This prevents the duplicate work of reimplementing the same business logic in both JavaScript and C# and maintains common strongly-typed interfaces across both sides. The original Saltarelle project was acquired by [Bridge.NET](https://github.com/bridgedotnet) in 2015 and discontinued in favor of their existing product which was not backwards compatible.  More recently, the Bridge.NET project announced it too has shut down.

This project aims to provide a set of utilities to assist in migrating an existing codebase from Saltarelle to TypeScript.

## Modern Alternatives

If you are starting a new project from scratch, you should definitely not be building it on top of Script#.  If you were considering reaching for Script#, you were probably trying to solve one of the following problems...

### Strongly-Typed Client Code and IDE Support

Strong typing eliminates certain classes of bugs from your programs and makes some aspects of maintaining and debugging code simpler.  Since JavaScript is not a strongly typed language, there have been many different attempts to add typing to JavaScript over the years ([Flow](https://flow.org/), [JS++](https://www.onux.com/jspp/), [PureScript](https://www.purescript.org/), etc, etc, etc). 

As of today, [TypeScript](https://www.typescriptlang.org/) is the most popular option for adding strong typing to JavaScript.  It has excellent library and IDE support and has the backing of Microsoft.  If all you are loking for is strong typing and good IDE support for your client-side code, this is all you need.

### Shared Client-Side and Server-Side Logic

It is common to have business logic which must be run on both the server-side and on the client-side of an application and be kept consistent across both (e.g. calculating whether a user has permission to perform an operation in order to show/hide the appropriate control on the client side; then also calculating it separately on the server side in order to enforce that a user is not able to bypass the client-side check).  If you are using a different programming language on the server-side vs the client-side, you will need to reimplement your logic twice and make sure to keep those implementations consistent over time.

Today, you can run JavaScript/TypeScript code on the server side using [NodeJS](https://nodejs.org/en/).  You can also run C# code on the client-side using [Blazor](https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor), which compiles C# code into WebAssembly.  If all you are looking for is to write logic once and have it able to run in both places, you have the option of writing it either in JavaScript/TypeScript or in C# using these tools.

_If you need/wish to write your client-side primarily in TypeScript and your server-side primarily in C# and still share logic between them, take a look at [nuget_npm_crossdeployment](https://github.com/pangaeatech/nuget_npm_crossdeployment)._ 

### Shared Client-Side and Server-Side Typing

Most applications share objects between the server-side and client-side code and send objects back and forth using serialization (e.g. [JSON](https://www.json.org/json-en.html)).  If you are using strong typing on both the client-side and server-side, you need to keep the type information consistent between both.   If you are using the same language on both the server-side and client-side (such as using NodeJS or Blazor as discussed above), then this is not a problem. 

However, if you need/wish to write your client-side code in TypeScript and your server-side code in C#, then the best approach is to have your C# server-side code generate an OpenAPI document detailing your types (using a tool such as [SwaggerGen](https://www.nuget.org/packages/Swashbuckle.AspNetCore.SwaggerGen/)) and then convert that into a TypeScript file using a tool such as [openapi-typescript](https://www.npmjs.com/package/openapi-typescript).
