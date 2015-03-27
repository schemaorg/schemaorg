**Schema.org project, current proposal repository**

This folders contains texts and "branches" with proposals that are in discussion, as Github *open issues* at  https://github.com/schemaorg/schemaorg/issues  

Process
=======

1. **Create** an issue here, to generate an *issue number*. <br/>Example: the issue "Transcribe equivalentProperty and Class mappings" creation, generated the *issue number 84*,  [`github.com/schemaorg/schemaorg/issues/84`](https://github.com/schemaorg/schemaorg/issues/84). 
2. **Discuss** the issue at public-vocabs@w3.org mail list and/or commenting at `github.com/schemaorg/schemaorg/issues/NUMBER`
3. (a collaborator with minimal `git` skills) **Consolidates** the proposal, with discussion results in a `Readme.md` text (and  in a modified source files when need), and submit it as a fork (new folder `testing/issueNUMBER`) of the `/proposals` folder at Github.
4. Review the `testing/issueNUMBER/Readme.md` with all  collaborators, like in a Wiki.
5. When the https://github.com/schemaorg *manager* agree that `testing/issueNUMBER` **is mature**, he/she decides: or accepts described changes; or move the folder to `stable/issueNUMBER` for hold (enhance with more serious tests and discussions).  

To merge more issues in a "main issue", rename the `testing/issueNUMBER` folder of the main issue to `testing/issueNUMBERetAl`, and document in the Readme the list of secondary issues.

Rationale
=========
People in the *Schema.org* discussions are coming from different fields and have different skills to collaborate, so, they are not obligated to know how to create `git`  branches... But they need some near or equal level of collaboration than a programmer with `git` skills.
The Github tools for "edit and commit" an `Readme.md` are the best will for this kind of broad collaboration. If you know how edit an issue, you know hou to edit a `Readme.md`.

Also the problem of **"to consolidate issue discussion in one document"** can be solved with the creation of the `/issueNUMBER/Readme.md` files.

