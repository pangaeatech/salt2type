## To migrate an existing Script# project to TypeScript:
1. Build the Script# project using Saltarelle in Debug mode:
    * `msbuild.exe Project.csproj /p:Configuration=Debug`
2. Build XML documentation using Doxygen:
    * Copy `Doxyfile` from salt2type into your project's directory
    * `doxygen Doxyfile`
    * `cd xml && xsltproc combine.xslt index.xml > all.xml`
3. Run `salt2type [JS] [XML] [DIR]` where:
    * `JS` = The (unminified) javascript file generated by Saltarelle
    * `XML` = The `all.xml` file generated by Doxygen
    * `DIR` = The folder to populate with the new typescript project