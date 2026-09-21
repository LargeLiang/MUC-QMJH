"""Checks for measurement boundaries, restricted tails and directional coding."""
import numpy as np
import pandas as pd
from revision01_analysis import count_format, prompt_hash, rcs, design, features, F, CRITERIA


def test_markdown_code_and_nested_format():
    s = '# title\n\n- **one**\n  - __two__\n\n```md\n# fake\n- **fake**\n```\n\n`**inline**`\n'
    assert count_format(s) == dict(header=1, list=2, bold=2)
    assert count_format('Setext\n======\n\n\\*\\*escaped\\*\\*') == dict(header=1,list=0,bold=0)
    assert count_format('<div>\n# fake\n**fake**\n</div>') == dict(header=0,list=0,bold=0)


def test_prompt_hash_preserves_code_indentation():
    assert prompt_hash(['a\r\nb']) == prompt_hash(['a\nb'])
    assert prompt_hash(['a\n b']) != prompt_hash(['a\nb'])
    assert prompt_hash(['a','b']) != prompt_hash(['a\nb'])


def test_rcs_linear_tails():
    knots=[-2,-.5,.5,2]
    np.testing.assert_allclose(rcs([-5,-4,-3],knots),0)
    np.testing.assert_allclose(np.diff(rcs([3,4,5],knots),n=2,axis=0),0,atol=1e-12)


def test_decisive_design_exchange_invariance():
    df=pd.DataFrame(dict(tokens_a=[100,200,150],tokens_b=[200,100,100],
                         header_a=[1,2,0],header_b=[3,1,1],list_a=[3,1,0],list_b=[1,2,2],
                         bold_a=[1,3,0],bold_b=[0,1,1],user_tokens=[10,20,30],turns=[1,2,1],
                         language=['en']*3,model_a=['A','B','A'],model_b=['B','A','A']))
    for k in ['cw','if','math','code']+CRITERIA: df[k]=[0,1,0]
    raw=features(df).abs(); scaling=pd.DataFrame({'mean':raw.mean(),'sd':raw.std(ddof=0)})
    rev=df.copy()
    for f in ['tokens','header','list','bold','model']:
        rev[f+'_a'],rev[f+'_b']=df[f+'_b'],df[f+'_a']
    pd.testing.assert_frame_equal(design(df,scaling,symmetric=True),design(rev,scaling,symmetric=True))
