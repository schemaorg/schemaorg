    window.addEventListener('load', function () {

        var branches = document.getElementsByClassName("dttBranch");
            for (var i = 0; i < branches.length; i++) {
                branches[i].addEventListener("click",dttBranchToggle);
            }    
        var focusTargets = [];
        focusTargets[0] = document.getElementsByClassName("dttLabel");
        focusTargets[1] = document.getElementsByClassName("dttLeaf");
        for(var t = 0; t < focusTargets.length;t++){
          var targ = focusTargets[t];
          for (var i = 0; i < targ.length; i++) {
              var children = targ[i].childNodes;
              for(j = 0; j < children.length;j++){
                var child = children[j];
                if(child.classList){
                  child.classList.add("dttFocusItem");
                  //child.tabIndex = 0;
                  child.addEventListener("keydown",dttLabelKey);
                }
              }
          }
        }   

        var dets = document.getElementsByClassName("dttDetails");
            for (var i = 0; i < dets.length; i++) {
                var det = dets[i];
                det.addEventListener("toggle",dttToggleCheck,i);
            }

        var sums = document.getElementsByTagName("summary");
        for(var i = 0; i < sums.length; i++){
          var sum = sums[i];
          sum.addEventListener("click",dttBranchToggle);
                
          var details = sum.parentNode;
          if(details.classList.contains("dttDetails")){
            sum.addEventListener("keydown",dttSummaryKey);
            sum.classList.add("dttFocusItem");
            //sum.tabIndex = 0;
          }
        }

        var bts = document.getElementsByClassName("ddtOpenAll");
        for (var i = 0; i < bts.length; i++) {
            bts[i].addEventListener("click",dttOpenClose);
        }    

        var bts = document.getElementsByClassName("ddtCloseAll");
        for (var i = 0; i < bts.length; i++) {
            bts[i].addEventListener("click",dttOpenClose);
        }    
    });

    function dttOpenClose(event){
      node = event.currentTarget;
      open = false;
      classes = node.classList;
      if(classes.contains("ddtOpenAll")){
        open = true;
      }
      if(classes.contains("ddtCloseAll")){
        open = false;
      }

      target = node.getAttribute("treeid");
      if(target){
        tree = document.getElementById(target);
        if(tree){
            openClose(tree, open);
        }
      }
    }

    function openClose(node, open){
        if (node.classList && node.classList.contains("dttDetails")){
            node.open = open
        }
        var kids = node.childNodes;
        for(var i=0;i < kids.length;i++){
            openClose(kids[i],open);
        }
    }

    function dttBranchToggle(event){
        node = event.currentTarget;
        var kids = node.childNodes;
        for(var i=0;i < kids.length;i++){
            kid = kids[i];
            classes = kid.classList;
            if(classes && classes.contains("dttDetails")){
                if (kid.open){
                    kid.open = false;
                    //kid.setAttribute("aria.expanded","false");
                }else{
                    kid.open = true;
                    //kid.setAttribute("aria.expanded","true")
                }
                break;
            }
        }
        event.stopPropagation();
    }

  var keyCode = Object.freeze({
      RETURN: 13,
      SPACE: 32,
      PAGEUP: 33,
      PAGEDOWN: 34,
      END: 35,
      HOME: 36,
      LEFT: 37,
      UP: 38,
      RIGHT: 39,
      DOWN: 40
  });

    function dttLabelKey(event){
      var key = event.keyCode;
      var node = event.currentTarget;
      var currentlimb = currentLimb(node);
      var branches = currentBranches(node);
      var pos = currenBranchPosition(node);
      var maxbranch = branches.length -1;
      var isLeaf = false;
      if (node.classList && node.classList.contains("dttLeaf")){
        isLeaf = true;
      }
      var target = null;
      switch (key) {
        case keyCode.RIGHT:
          if(!isLeaf){
            focusOnBranchSummary(currentlimb,node);
          }
          break;
        case keyCode.UP:
          if(pos > 0){
            target = branches[Math.max(0,pos - 1)];
          }else if(pos == 0){
            var parent = parentBranch(node);
            focusOnBranchSummary(parent,node);
          }
          break;
        case keyCode.DOWN:
          target = branches[Math.min(pos + 1, maxbranch)];
          break;
        case keyCode.END:
          target = branches[maxbranch];
          break;
        case keyCode.HOME:
          target = branches[0];
          break;
      }
      if(target){
        focusOnBranchLabel(target,node);
      }
    }

    function dttSummaryKey(event){
        var key = event.keyCode;
        var node = event.currentTarget;
        var currentlimb = currentLimb(node);
  
        var details = node.parentNode;
        if(details.classList.contains("dttDetails")){
            switch (key) {
                case keyCode.RETURN:
                case keyCode.RIGHT:
                case keyCode.DOWN:
                    if(!details.open){
                        details.open = true;
                    }else{
                      focusOnTree(limbSubTree(currentlimb),node);
                    }
                    break;
                case keyCode.UP:
                case keyCode.LEFT:
                    if(details.open){
                        details.open = false;
                      }else{
                        focusOnBranchLabel(currentlimb,node);
                      }
                    break;
            }
        }
    }
  

  function currentLimb(node){
    var limb = null;
    var parent = node;
    while(parent){
      var classList = parent.classList;
      if(classList && classList.contains("dttLabel")){
        limb = parent.parentNode;
        break;
      }else if(classList && (classList.contains("dttLeaf") || classList.contains("dttBranch"))){
        limb = parent;
        break;
      }
      parent = parent.parentNode;
    }
    return limb;
  }

  function parentBranch(node){
    var current = currentLimb(node);
    parenttree = currentTree(current.parentNode)
    var classList = parenttree.classList;
    if(classList && classList.contains("dttTree")){
      return current;
    }
    return currentLimb(current.parentNode);
  }
  
  function currentTree(node){
      var Tree = null;
      var parent = node;
      while(parent){
        var classList = parent.classList;
        if(classList && (classList.contains("dttSubTree")|| classList.contains("dttTree")) ){
          Tree = parent;
          break;
        }
        parent = parent.parentNode;
      }
      return Tree;
    }

    function limbSubTree(limb){
      var classList = limb.classList;
      if(classList && classList.contains("dttBranch")){
        var children = limb.childNodes;
        for(var i = 0; i < children.length; i++){
          var child = children[i];
          var cclassList = child.classList;
          if(cclassList && cclassList.contains("dttDetails")){
            var items = child.childNodes;
            for(var j=0;j<items.length;j++){
              var it = items[j];
              var iclassList = it.classList;
              if(iclassList && iclassList.contains("dttSubTree")){
                return items[j];
                break;
              }
            }
          }
        }
      }
    }

    function classInChildren(classname,node){
      var children = node.childNodes;
      for(var i =0;i <children.length;i++){
        var child = children[i];
        var classList = child.classList;
        if(classList && classList.contains(classname)){  
          return child;
        }
        ret = classInChildren(classname,child);
        if(ret){
          return ret;
        }
      }
      return null;
    }

    function parentTree(tree){
      ret = null;
      var classList = tree.classList;
      if(classList && classList.contains("dttSubTree")){
        ret = currentTree(tree.parentNode);
      }
      return ret;
    }

    function treeBranches(tree){
      var branches = [];
      for(var i = 0;i < tree.childNodes.length;i++){
        var ti = tree.childNodes[i]
        if(ti.classList &&  (ti.classList.contains("dttLeaf") || ti.classList.contains("dttBranch"))){
          branches.push(ti);
        } 
      }
      return branches ;
    }

    function currentBranches(node){
      var tree = currentTree(node);
      return treeBranches(tree);
    }

    function branchPosition(branches,branch){
      var pos = -1;
      for(var i =0;i< branches.length;i++){
        if(branches[i] === branch){
          pos = i;
          break;
        }
      }
      return pos;
    }

    function currenBranchPosition(node){
      var currentBranch = currentLimb(node);
      var branches = currentBranches(node);
      return branchPosition(branches,currentBranch);
    }

    function focusOnBranchSummary(branch,currentNode){
      if(currentNode === undefined){
        currentNode = null;
      }
      var target = null;
      var children = branch.childNodes;
      for(var i = 0; i < children.length; i++){
        var child = children[i];
        var classList = child.classList;
        if(classList && classList.contains("dttDetails")){
          var items = child.childNodes;
          for(var j=0;j<items.length;j++){
            var it = items[j];
            if(it.tagName == "SUMMARY"){
              target =  items[j];
              break;
            }
          }
        }
        if(target){
          break;
        }
      }
     if(target){
        moveFocus(target,currentNode);
      }
    }

    function focusOnBranchLabel(branch,currentNode){
      if(currentNode === undefined){
        currentNode = null;
      }
      var target = null;
      var children = branch.childNodes;
      var bclassList = branch.classList;
      if(bclassList &&  bclassList.contains("dttLeaf")){
        for(var i =0; i < children.length;i++){
          var child = children[i];
          var classList = child.classList;
          if(classList &&  classList.contains("dttFocusItem")){
            target = child;
            break;
          }
        }
      }else{
        for(var i = 0; i < children.length; i++){
          var child = children[i];
          var classList = child.classList;
          if(classList &&  classList.contains("dttLabel")){
            var items = child.childNodes;
            for(var j=0;j<items.length;j++){
              t = items[j];
              if(t.classList &&  t.classList.contains("dttFocusItem")){
                target =  t;
                break;
              }
            }
          }
          if(target){
            break;
          }
        }
      }
      if(target){
        moveFocus(target,currentNode);
      }
    }

    function focusOnTree(tree,currentNode){
      var branches = treeBranches(tree);
      var firstBranch = branches[0];
      focusOnBranchLabel(firstBranch,currentNode)
    }

    function moveFocus(node,currentNode){
      if(currentNode === undefined){
        currentNode = null;
      }  
      node.focus();
      //node.tabIndex = 0;
      //if(currentNode){
        //currentNode.tabIndex = 0;
      //}
    }
    


    function dttToggleCheck(event){
        node = event.currentTarget;
        var state = "treeclosed";
        if(node.open){
            state = "treeopen"
        }
        var parent = node.parentNode;
        var parentBranch = null;
        while (parent){
            if (parent.classList.contains("dttBranch")){
                parentBranch = parent;
                break;
            }
        }
        if(parentBranch){
            parentBranch.setAttribute("dttState",state)
        }
    }

    function dttOpenParents(id){
      var target = id.getAttribute('href');
      target = target.substring(1);
      targetNode = document.getElementById(target);
    
      var parent = targetNode.parentNode;
      while (parent){
        if (parent.classList && parent.classList.contains("dttTree")){
          break;
        }
        if (parent.classList && parent.classList.contains("dttDetails")){
          parent.open = true;
        }
        parent = parent.parentNode;
      }
    }
