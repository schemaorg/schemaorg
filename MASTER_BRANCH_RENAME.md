# Schema.org

## Renaming Master Branch 

In the [Schema.org Github Repository](https://github.com/schemaorg/schemaorg) the previously default branch name of **master** has been replaced with a new default branch name of **main**. (_See issue [#2668](https://github.com/schemaorg/schemaorg/issues/2668) for background to this change_)

This work, carried out on 23rd July 2020, should have no impact on developers working from the Github user interface. All non-merged Pull Requests for merges into the *master* branch have been updated to merged into the newly created *main* branch.

**Impact on developers working in a local** ***master*** **branch copy**

To bring your local copy into line with the renamed branch in the repository, follow these steps:

1. Fetch the latest branches from the remote.  
```git fetch --all```  


2. Update the upstream remote's HEAD.  
```git remote set-head origin -a```  


3. Switch your local branch to track the new remote branch.  
```git branch --set-upstream-to origin/main```  


4. Rename your branch locally.  
```git branch -m master main```  



