# -*- mode: python -*-

block_cipher = None


a = Analysis(['Perception_Mapping.py'],
             pathex=['C:\\Users\\cohend1\\Desktop\\PA'],
             binaries=[],
             datas=[],
             hiddenimports=['pandas._libs.tslibs.np_datetime','pandas._libs.tslibs.nattype','pandas._libs.skiplist','pandas._libs.tslibs.timedeltas'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Perception_Mapping',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
