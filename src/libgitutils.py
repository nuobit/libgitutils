import os
import subprocess
import re
import sys

def exec_cmd(*params):
    proc1 = subprocess.Popen(
            params,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
 
    outs, errs = proc1.communicate(timeout=None)
    if outs==b'':
        outs = None
    else:
        outs = outs.decode('utf-8').strip()
        
    if errs==b'':
        errs = None
    else:
        errs = errs.decode('utf-8').strip()
        
    return outs, errs
    
class GitFolder:
    def __init__(self, folder):
        self.folder = folder.rstrip("/")
                
    def __repr__(self):
        #return "<%s %s branch: %s commit: %s at %i>" % (self.__class__.__name__, self.folder, self.get_current_branch(), self.get_current_commit(), id(self))
        return "<%s %s at %i>" % (self.__class__.__name__, self.folder, id(self))
    
    def git(self, *params):
        # forcem a que lidioma sigui sempre angles per tal que els misstages que retorna empre siguin el smateixos indepoendentment
        # dela amuina on sexecutein
        os.putenv('LANG', 'en_US.UTF-8')
        os.putenv('LANGUAGE', 'en_US.UTF-8')
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LANGUAGE'] = 'en_US.UTF-8'
        
        out, errs = exec_cmd('git', '-C', self.folder, *params)
        
        return out, errs
        
    def is_git_repo(self):
        out, errs = self.git('log')
        if errs is not None:
            if errs.startswith("fatal: Not a git repository"):
                return False
            else:
                 raise Exception("unexpected 1!! '%s'" % (errs, ))
        else:
            if out.startswith("commit"):
                return True
            else:
                raise Exception("unexpected 2!! '%s'" % (out, ))
        
    def get_current_branch_old(self):
        out, errs = self.git('branch')
        if errs is None:
            m = re.search(r"\* (.+)$", out)
            if m is None:
                raise Exception("unexpected!!! %s " % out)
            return m.group(1)
        else:
            raise Exception("unexpected\n%s" % errs)
            
    def get_current_branch(self):
        out, errs = self.git('rev-parse', '--abbrev-ref', 'HEAD')
        if errs is None:
            return out
        else:
            raise Exception("unexpected\n%s" % errs)

    def get_current_commit(self):
        out, errs = self.git('rev-parse', 'HEAD')
        if errs is None:
            if len(out)!=40:
                raise Exception("unexpected long\n%s (%i)" % (out, len(out)))
            return out
        else:
            raise Exception("unexpected\n%s" % errs)
            
    def get_diff_files(self):
        ''' retorna els fitxers modificats en local i els afegits. no diu els fitxrs renombrats com a.bak '''
        out, errs = self.git('ls-files', '--exclude-standard', '--modified', '--other')
        if errs is not None:
            if errs.startswith("error: "):
                raise Exception(errs)
            else:
                raise Exception("unexpected\nout: %s\nerr: %s" % (out, errs))
        else:
            if out is None:
                return []
            else:
                #return [self.folder + '/' + x for x in out.split("\n")]
                return list(filter(lambda x: not x.lower().endswith('.pyc'), out.split("\n")))

    def has_upstream(self):
        out, errs = self.git('remote')
        if errs is None:
            remotes = out.split('\n')
            return 'upstream' in remotes
        else:
            raise Exception("unexpected\n%s" % errs)
            
    def fetch_upstream(self, check=True):
        if check and not self.has_upstream():
            raise Exception("Remote repository 'upstream' not found")
        out, errs = self.git('fetch', 'upstream')
        if errs is not None:
            if not errs.startswith("From "):
                raise Exception("unexpected\n%s" % errs)
        else:
            errs = 'Already fetched'
        if out is not None:
            raise Exception("unexpected\n%s" % out)
            
        return errs
    
    def merge_upstream(self, check=True):
        if check and not self.has_upstream():
            raise Exception("Remote repository 'upstream' not found")
    
        cur_branch = self.get_current_branch()
        m = re.search('[0-9]+\.[0-9]+',cur_branch)
        if m is None:
            raise Exception("Current branch version could not be extracted %s" % cur_branch)
        upstream_branch = m.group(0)
        
        out, errs = self.git('merge', 'upstream/%s' % upstream_branch, '--no-edit')
        if errs is not None:
            raise Exception("%s" % errs)
        if out is None:
            raise Exception("Unexpected\n%s" % out)
        
        return out
            
    def push(self):
        out, errs = self.git('push')
        if errs is None:
            return out
        else:
            if errs!="Everything up-to-date":
                if not errs.startswith("To "):
                    raise Exception("Unexpected\n%s" % repr(errs))
            return errs
        
    def pull(self):
        out, errs = self.git('pull')
        if errs is None:
            if out!="Already up-to-date.":
                raise Exception("Unexpected\n%s" % errs)
            else:
                return out
        else:
            if errs.startswith("From "):
                return "%s\n%s" % (errs, out)
            else:
                if errs.startswith("fatal: No remote repository specified."):
                    return "WARNING: Local repository has not a remote one defined -> It won't be updated."
                else:
                    raise Exception("Unexpected\n%s" % repr(errs))
                
    @classmethod
    def find_git_folders(cls, folder, level=0):
        ''' retorna una llista d'objectes GitFolder amb els gitfolders trobats dins la carpta folder'''
        if not folder.endswith("/"):
            folder+="/"
        
        git_tmp = cls(folder)
        if git_tmp.is_git_repo():
            return [git_tmp]
        else:
            # esborrem l'objecte tepmoral creat, per alliberar memoria en cas que no ho faci el GC
            del git_tmp
            _, dirs, _ = next(os.walk(folder))
            a=[]
            for d1 in dirs:
                a+=cls.find_git_folders(folder + d1, level+1)
            return a


def gitpull():
    def n(s):
        if '\n' not in s:
            return s
        else:
            return '\n' + s

    #curdir = os.path.dirname(os.path.realpath(__file__))
    curdir = os.getcwd()
    print("**** Searching git folders ******")

    gits = GitFolder.find_git_folders(curdir)
    for g in gits:
        print("---- Searching changes for %s -----" % g.folder)
        branch0, commit0 = g.get_current_branch(), g.get_current_commit()
        if '--upstream' in sys.argv and g.has_upstream():
            res = g.fetch_upstream(check=False)
            print("* Fetch upstream: " + n(res))
            res = g.merge_upstream(check=False)
            print("* Merge upstream: " + n(res))
            res = g.push()
            print("* Push: " + n(res))
        else:
            res = g.pull()
            print("* Pull: " + n(res))
        branch1, commit1 = g.get_current_branch(), g.get_current_commit()
        if branch0 != branch1 or commit0 != commit1:
            print("* " + "Branch: %s -> %s, Commit: %s -> %s" % (branch0, branch1, commit0, commit1))