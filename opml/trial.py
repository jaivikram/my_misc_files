import opml 
from xml.dom.minidom import Document
empty_branches = []
doc = Document()

def traverse(node, tabs, parent, cn):
    l = len(node)
    ele = doc.createElement("outline")
    for attr in ['title', 'xmlUrl', 'htmlUrl', 'type']:
        if hasattr(node, attr):
            ele.setAttribute(attr, getattr(node, attr))
    if l != 0: 
        sum = 0
        title = 'root'
        try:
            title = node.title
            if node.title.startswith('['):
                sum = int(node.title[1])
                title = ' '.join(node.title.split(' ')[1:])
        except:
            pass
        for sn in node:
            sum = sum + traverse(sn, tabs+1, parent+' : '+title, ele)
        node.title = '['+str(sum)+'] ' + title
        ele.setAttribute('title', node.title)
        #print(sum)
        #f.write('\t'*tabs+node.title+'\n')        
        #if tabs == 2:
        #    f.write('-'*50+'\n')
        cn.appendChild(ele)
        return sum
    else:
        #print(node.title)
        cn.appendChild(ele)
        if hasattr(node, 'xmlUrl'):
            return 1
        else: 
            empty_branches.append(parent + ' : ' + node.title)
            return 0


if __name__ == '__main__':
    root = opml.parse('./taxonomy_scrubbed.opml')
    f = file('taxonomy.txt', 'w')
    traverse(root, 0, 'root', doc)
    fp = file('result.xml', 'w')
    fp.write(doc.toprettyxml(indent = " "))
    fp.close()
    #f.write("\n\n+++++++++++++++++++++++++++++++++++++++\n\n")
    f.writelines([each+'\n' for each in empty_branches])
    f.close()

#def getIPAndDomains(filename):
#    mail = email.message_from_file(file('hardham/'+filename))
#    body = [each.get_payload() for each in mail.get_payload()]
#    headers = mail.items()
#    iprex = "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
#    domainrex = ""
#	pass


